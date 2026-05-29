from __future__ import annotations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister


H2_TOY_COEFFS = {
    "constant": -1.052373245772859,
    "z0": 0.39793742484318045,
    "z1": -0.39793742484318045,
    "z0z1": -0.01128010425623538,
    "x0x1": 0.18093119978423156,
}


def build_ansatz(theta: float, basis: str = "z") -> QuantumCircuit:
    qreg = QuantumRegister(2, "q")
    creg = ClassicalRegister(2, "meas")
    circuit = QuantumCircuit(qreg, creg)
    circuit.ry(theta, qreg[0])
    circuit.cx(qreg[0], qreg[1])
    if basis == "x":
        circuit.h(qreg[0])
        circuit.h(qreg[1])
    circuit.measure(qreg, creg)
    return circuit
