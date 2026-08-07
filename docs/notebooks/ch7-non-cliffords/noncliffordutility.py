import stim
import time
import numpy as np
import matplotlib.pyplot as plotter; plotter.rcParams['font.family'] = 'Monospace'
from typing import List
import cirq

def cluster_state_stim(n_qubits: int) -> stim.Circuit:
    """
    Prepares an n-qubit 1D cluster state stim circuit:

    """
    c = stim.Circuit()

    for q in range(n_qubits):
        c.append("H", q)

    for q in range(n_qubits - 1):
        c.append("CZ", [q, q + 1])

    return c

def tableau_simulator_expectation_K0(n_qubits: int) -> float:
    """
    'Analytical-like' estimate of stabilizer expectation value <K0> = <X0 Z1> using Stim's TableauSimulator.
    For a perfect cluster state, the expectation value is +1.

    """
    simulator = stim.TableauSimulator()
    
    simulator.do(cluster_state_stim(n_qubits))    
    simulator.do(stim.Circuit("H 0")) # Rotate X0 into Z0 via H

    b0 = simulator.measure(0)  
    b1 = simulator.measure(1)

    # {0,1} -> {-1,+1}
    x0 = 1 - 2 * b0  
    z1 = 1 - 2 * b1  

    return x0 * z1   # <X0 Z1>

def time_cluster_stim(n: int, shots: int):
    """
    Returns times for `compile_sampler()` with corresponding expectation value `<X0Z1>`.
    
    """

    c = cluster_state_stim(n)
    
    c.append("H", 0)
    c.append("M", [0, 1])
    
    t0 = time.perf_counter()
    sampler = c.compile_sampler()
    samples = sampler.sample(shots=shots)
    t1 = time.perf_counter()
    t_compile = t1 - t0

    x0 = 1 - 2 * samples[:, 0].astype(int)
    z1 = 1 - 2 * samples[:, 1].astype(int)

    exp_val_compiled = float(np.mean(x0 * z1))

    return t_compile, exp_val_compiled

def run_stim_sweep(n_list: List[int], shots: int = 10_000):
    """
    Run a sweep of the Stim circuit for the cluster state with measurements on qubits 0 and 1 for different numbers of qubits.
    """
    compile_times = []
    exp_vals = []

    for n in n_list:
        t_comp, exp_val_compiled = time_cluster_stim(n, shots=shots)
        compile_times.append(t_comp)
        exp_vals.append(exp_val_compiled)

        print(
            f"[STIM] n_qubits={n:6d}  "
            f"t_compile={t_comp:.3e} s  "
            f"<X0Z1>={exp_val_compiled:+.6f}  "
        )

    return (
        np.array(n_list, dtype=float),
        np.array(compile_times, dtype=float),
        np.array(exp_vals, dtype=float),
    )


def make_1d_cluster_with_T_cirq(n: int, add_T: bool = False):
    """
    Cirq circuit: N-qubit 1D cluster with a T on every qubit.
    """
    
    qubits = cirq.LineQubit.range(n)
    circuit = cirq.Circuit()

    # |+>^⊗n
    circuit.append(cirq.H.on_each(*qubits))

    # 1D CZ chain
    for i in range(n - 1):
        circuit.append(cirq.CZ(qubits[i], qubits[i + 1]))

    
    if add_T:
        circuit.append(cirq.T.on_each(*qubits))

    return circuit, qubits


def time_cluster_cirq_with_T(n_qubits: int):
    """
    Returns times for `simulate_expectation_values()` with corresponding expectation value `<X0Z1>`.
    """
    circuit, qubits = make_1d_cluster_with_T_cirq(n_qubits, add_T=True)
    simulator = cirq.Simulator()

    if n_qubits < 2:
        raise ValueError("Need at least 2 qubits to define X0 Z1.")

    obs = cirq.X(qubits[0]) * cirq.Z(qubits[1])

    # Exact expectation
    t0 = time.perf_counter()
    [exp_val] = simulator.simulate_expectation_values(
        circuit, observables=[obs]
    )
    t1 = time.perf_counter()
    t_sim = t1 - t0

    return float(exp_val.real), t_sim

def run_cirq_T_sweep(n_list: List[int]):
    """
    Runs a sweep of the Cirq circuit for the cluster state with T gates for different numbers of qubits.
    """
    exact_times = []
    exact_exps = []

    for n_qubits in n_list:
        exp_val, t_sim = time_cluster_cirq_with_T(
            n_qubits
        )
        exact_times.append(t_sim)
        exact_exps.append(exp_val)

        print(
            f"[CIRQ+T] n_qubits={n_qubits:3d}  "
            f"t_sim={t_sim:.3e} s  "
            f"<X0Z1>_sim={exp_val:+.6f}  "
        )

    return (
        np.array(n_list, dtype=float),
        np.array(exact_times, dtype=float),
        np.array(exact_exps, dtype=float),
    )
