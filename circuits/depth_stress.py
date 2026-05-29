from __future__ import annotations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister


def build_depth_stress_ghz(depth_layers: int) -> QuantumCircuit:
    qreg = QuantumRegister(4, "q")
    creg = ClassicalRegister(4, "meas")
    circuit = QuantumCircuit(qreg, creg)
    circuit.h(qreg[0])
    circuit.cx(qreg[0], qreg[1])
    circuit.cx(qreg[1], qreg[2])
    circuit.cx(qreg[2], qreg[3])
    for layer in range(depth_layers):
        angle = 0.03125 * (layer + 1)
        for qubit in range(4):
            circuit.rz(angle, qreg[qubit])
            circuit.sx(qreg[qubit])
        circuit.cx(qreg[0], qreg[1])
        circuit.cx(qreg[2], qreg[3])
    circuit.measure(qreg, creg)
    return circuit
