"""
Lattice surgery primitives (merge + split)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set

Coord = Tuple[int, int]

# Commutations
PAULI_TABLE: Dict[Tuple[str, str], str] = {
    ("I","I"): "I", ("I","X"): "X", ("I","Z"): "Z", ("I","Y"): "Y",
    ("X","I"): "X", ("X","X"): "I", ("X","Z"): "Y", ("X","Y"): "Z",
    ("Z","I"): "Z", ("Z","X"): "Y", ("Z","Z"): "I", ("Z","Y"): "X",
    ("Y","I"): "Y", ("Y","X"): "Z", ("Y","Z"): "X", ("Y","Y"): "I",
}

def apply_error(coord: Coord, op: str, error_state: Dict[Coord, str]) -> None:
    """Left-multiply a Pauli error onto a data qubit in `error_state`."""
    error_state[coord] = PAULI_TABLE[(error_state[coord], op)]


# Work in global co-ordinate system
def stab_kind_from_coord(sx: int, sz: int) -> str:
    """(s_x + s_z) % 4 == 2: stabilizer is Z, else X."""
    return "Z" if (sx + sz) % 4 == 2 else "X"


def data_coords(d: int, offset: int) -> List[Coord]:
    """Data qubits are even-even on [offset..offset+2(d-1)] step 2."""
    min_d = offset
    max_d = offset + (2 * (d - 1))
    return [(x, z) for x in range(min_d, max_d + 1, 2) for z in range(min_d, max_d + 1, 2)]


def stabilizers_local(d: int, offset: int, namespace: str, mirror_z: bool = False) -> Dict[str, dict]:
    """
    Generate stabilizers (odd-odd coordinates) including boundary mask (rotated code).
    Returns dict: stab_id -> {"coord":(sx,sz), "kind":..., "neighbors":[(x,z)], "active":True}
    Note: `mirror_z` does NOT change which stabilizers exist; mirroring is applied at Patch mapping time.
    """
    data = set(data_coords(d, offset))
    min_d = offset
    max_d = offset + (2 * (d - 1))

    stabs: Dict[str, dict] = {}
    for sx in range(min_d - 1, max_d + 2, 2):
        for sz in range(min_d - 1, max_d + 2, 2):
            candidates = [(sx - 1, sz - 1), (sx - 1, sz + 1), (sx + 1, sz - 1), (sx + 1, sz + 1)]
            neighbors = [p for p in candidates if p in data]
            if len(neighbors) not in (2, 4):
                continue

            # boundary mask
            if len(neighbors) == 2:
                if sx == min_d - 1:
                    if sz % 4 != 1:
                        continue
                elif sx == max_d + 1:
                    if sz % 4 != 3:
                        continue
                elif sz == min_d - 1:
                    if sx % 4 != 3:
                        continue
                elif sz == max_d + 1:
                    if sx % 4 != 1:
                        continue
                else:
                    continue

            kind = stab_kind_from_coord(sx, sz)
            sid = f"{namespace}_{kind}_{sx}_{sz}"
            stabs[sid] = {"coord": (sx, sz), "kind": kind, "neighbors": neighbors, "active": True}
    return stabs


def measure_stab(kind: str, neighbors_global: List[Coord], error_union: Dict[Coord, str]) -> int:
    """
    Ideal stabilizer measurement given current Pauli errors:
    returns 0 for +1, 1 for -1.
    """
    parity = 0
    for q in neighbors_global:
        err = error_union.get(q, "I")
        if kind == "Z" and err in ("X", "Y"):
            parity ^= 1
        elif kind == "X" and err in ("Z", "Y"):
            parity ^= 1
    return parity


# define patch and merge/split primitives
class Patch:
    def __init__(self, name: str, d: int, offset: int, place: Coord = (0, 0), mirror_z: bool = False):
        self.name = name
        self.d = d
        self.offset = offset
        self.min_d = offset
        self.max_d = offset + (2 * (d - 1))
        self.place_x, self.place_z = place
        self.mirror_z = mirror_z

        self.data_local = data_coords(d, offset)
        self.data_global = [self.local_to_global(p) for p in self.data_local]
        self.data_global_set: Set[Coord] = set(self.data_global)

        self.error: Dict[Coord, str] = {p: "I" for p in self.data_global}

        self.stabs_local = stabilizers_local(d, offset, namespace=name, mirror_z=mirror_z)
        self.active_stabs: Set[str] = set(self.stabs_local.keys())

    def local_to_global(self, coord: Coord) -> Coord:
        x, z = coord
        if self.mirror_z:
            z = self.min_d + self.max_d - z
        return (x + self.place_x, z + self.place_z)

    def stab_global(self, stab: dict) -> Tuple[int, int, str, List[Coord], int]:
        sx, sz = stab["coord"]
        if self.mirror_z:
            sz = self.min_d + self.max_d - sz
        gsx, gsz = (sx + self.place_x, sz + self.place_z)
        neigh_g = [self.local_to_global(p) for p in stab["neighbors"]]
        return (gsx, gsz, stab["kind"], neigh_g, len(neigh_g))


class SurgerySession:
    """
    Two-patch Z-merge along +z direction (horizontal axis is z).
    Creates seam stabilizers at seam_z and disables touching z-edge boundary stabilizers.
    """
    def __init__(self, q_patch: Patch, p_patch: Patch, gap: int = 2):
        self.q = q_patch
        self.p = p_patch
        self.gap = gap
        self.merge_on = False
        self.seam_stabs: Dict[str, dict] = {}
        self.disabled: Set[str] = set()

    def error_union(self) -> Dict[Coord, str]:
        u: Dict[Coord, str] = {}
        u.update(self.q.error)
        u.update(self.p.error)
        return u

    def toggle_merge(self) -> None:
        if not self.merge_on:
            self._merge_on()
        else:
            self._merge_off()
        self.merge_on = not self.merge_on

    def _merge_on(self) -> None:
        # merging along z,  disable boundary stabs on touching z-edges
        q_edge_z = self.q.max_d + 1
        p_edge_z = (self.p.max_d + 1) if self.p.mirror_z else (self.p.min_d - 1)

        for sid, stab in self.q.stabs_local.items():
            if sid in self.q.active_stabs and len(stab["neighbors"]) == 2 and stab["coord"][1] == q_edge_z:
                self.q.active_stabs.remove(sid)
                self.disabled.add(sid)

        for sid, stab in self.p.stabs_local.items():
            if sid in self.p.active_stabs and len(stab["neighbors"]) == 2 and stab["coord"][1] == p_edge_z:
                self.p.active_stabs.remove(sid)
                self.disabled.add(sid)

        # seam at z = q_max_data_z + 1
        q_max_gz = max(z for (x, z) in self.q.data_global)
        seam_z = q_max_gz + 1

        q_min_gx = min(x for (x, z) in self.q.data_global)
        q_max_gx = max(x for (x, z) in self.q.data_global)

        data_union = self.q.data_global_set | self.p.data_global_set

        # create both X and Z seam stabilizers
        self.seam_stabs = {}
        for sx in range(q_min_gx + 1, q_max_gx + 2, 2):
            sz = seam_z
            candidates = [(sx - 1, sz - 1), (sx - 1, sz + 1), (sx + 1, sz - 1), (sx + 1, sz + 1)]
            neigh = [p for p in candidates if p in data_union]
            if len(neigh) not in (2, 4):
                continue

            kind = stab_kind_from_coord(sx, sz)
            sid = f"m_{kind}_{sx}_{sz}"
            self.seam_stabs[sid] = {"coord": (sx, sz), "kind": kind, "neighbors": neigh, "active": True}

    def _merge_off(self) -> None:
        for sid in list(self.disabled):
            if sid.startswith(self.q.name + "_"):
                self.q.active_stabs.add(sid)
            elif sid.startswith(self.p.name + "_"):
                self.p.active_stabs.add(sid)
        self.disabled.clear()
        self.seam_stabs = {}


def logical_ZZ_eigenvalue(session: SurgerySession) -> Optional[int]:
    """Compute Z⊗Z eigenvalue (+1/-1) from seam Z-check outcomes (when merge_on)."""
    if not session.merge_on:
        return None
    err_u = session.error_union()
    bit = 0
    for _, stab in session.seam_stabs.items():
        if stab["kind"] != "Z":
            continue
        bit ^= measure_stab("Z", stab["neighbors"], err_u)
    return +1 if bit == 0 else -1
