# Deltakit Textbook: A hands-on introduction to Quantum Error Correction (QEC) concepts

Written by the Riverlane team and friends. 

This repository contains the files for the textbook which appears at [textbook.riverlane.com](https://textbook.riverlane.com/).

## Motivation

Quantum error correction (QEC) is a key ingredient that is necessary for unlocking the full potential of quantum computers. To build large-scale error-corrected quantum computers with hundreds to thousands of logical qubits running millions to billions of operations, we will need the participation of experts across various disciplines, and they will all need to upskill in QEC. Today, QEC talent is rare, and is the most commonly reported challenge as quantum computing teams begin their journeys toward fault tolerance.

This textbook aims to bridge the gap between **the understanding** of QEC and **the practice** of QEC. The core principles for the textbook are:

- **Hands-on** to encourage experimentation with QEC, and enable the learner to reproduce recent research results using state-of-the-art QEC tools,
- **Detailed**, showing every step at first before using an advanced QEC tool that hides all the details, so that learners understand the nuances of QEC,
- **Interactive**, so that readers can experiment while reading the textbook,
- **Open-source**, so that QEC experts can enable QEC learners by contributing modern QEC concepts to the textbook.

## Prerequisites
The pedagogy in the textbook assumes that a reader is familiar with quantum states, gates, circuits, and measurements. We also assume familiarity with the matrix manipulation associated with quantum circuits, and the matrices for the Pauli gates.

## How to best use this textbook for self-learning
There are several places where one can obtain a deep understanding of QEC concepts. However, fully detailed implementation of the quantum circuits in QEC is not widely available. For this reason, this hands-on textbook is best used as a supplement to another textbook that provides grounding in the principles of QEC. Some recommended resources:

- Dan Browne's [Lectures on Topological Codes and Quantum Computation](https://sites.google.com/site/danbrowneucl/teaching/lectures-on-topological-codes-and-quantum-computation)
- John Preskill's [Ph219 lecture notes](https://www.preskill.caltech.edu/ph219/) (particularly Chapter 7)
- Daniel Gottesman's [PhD dissertation on Stabilizer Codes and Quantum Error Correction](https://arxiv.org/pdf/quant-ph/9705052)

## How to best use this textbook in a quantum computing course
The first few weeks of a typical first quantum computing course cover concepts such as qubits and quantum states, gates, measurements, quantum circuits, and circuit identities. Then, the coursework typically branches toward various directions – for example, sometimes they continue toward extensive discussion of quantum algorithms, or focus on surveying the physics of quantum devices and systems.

The content in this textbook is designed to address the gap between QEC theory and QEC practice. For this reason, it can be used as another branch after the first few weeks of a first quantum computing course, assuming that it is coupled with one of the resources mentioned above.

## Contributing to the textbook
Anyone is welcome to contribute to the textbook! All contributors will be credited in the contributors list of the Deltakit Textbook and on the specific chapters that they write.

Here is a list of topics that are currently looking for contributors

| Topic | Contributor |
| :----- | :----- |
| Long-range interactions and qLDPC codes | TBD |
| Transversal logic (Logical cliffords, lattice surgery, magic state distillation) | [Srushti Patil](https://github.com/Next-di-mension/deltakit-textbook/) |
| Specialized decoders | TBD |
| Color codes | TBD |
| Bicycle Bivariate (BB) codes | TBD |
| Hypergraph product codes | TBD |
| Flag gadgets | TBD |
| ZX Calculus and error propagation | [Lia Yeh](https://github.com/lia-approves/deltakit-textbook/) |
| Considerations of QEC experiments on real systems | TBD |
| Hook errors in practice | TBD |
| Real-time QEC | TBD |
| Noise models 101 (eg coherent errors, readout errors) | TBD |
| Threshold theorems | TBD |
| Decoder library additions | TBD |

If you have an idea for a contribution that does not appear in the list above, we encourage you to create an issue tagged as a contribution to discuss the parameters of the contribution before spending the time creating it. Issues will auto-tag a member of the Riverlane team who will pull in the right experts to guide the contribution to completion.

Every contribution is assigned a reviewer at Riverlane who will check for factual consistency and clarity. 

### Build instructions

You can build the textbook locally as you are adding or improving content. To do so, we recommend installing `uv`:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then build the docs like so:

```
uvx nox -s docs
```

## Contact

You can contact abraham.asfaw@riverlane.com for topics related to the textbook including usage in coursework,
suggestions for new content or pedagogy improvements.
