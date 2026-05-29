from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_kernel import AegisContinuityKernel, EnvironmentVector, NodeTelemetry, normalize_vector
from examples.ibm_bridge import extract_sampler_counts, require_qiskit_core, require_runtime, select_real_backend


H2_TOY_COEFFS = {
    "constant": -1.052373245772859,
    "z0": 0.39793742484318045,
    "z1": -0.39793742484318045,
    "z0z1": -0.01128010425623538,
    "x0x1": 0.18093119978423156,
}


def build_ansatz(theta: float, basis: str = "z") -> Any:
    classical_register, quantum_circuit, quantum_register, _ = require_qiskit_core()
    qreg = quantum_register(2, "q")
    creg = classical_register(2, "meas")
    circuit = quantum_circuit(qreg, creg)
    circuit.ry(theta, qreg[0])
    circuit.cx(qreg[0], qreg[1])
    if basis == "x":
        circuit.h(qreg[0])
        circuit.h(qreg[1])
    circuit.measure(qreg, creg)
    return circuit


def parity_expectation(counts: dict[str, int], qubits: int = 2) -> float:
    total = max(1, sum(int(value) for value in counts.values()))
    acc = 0.0
    for bitstring, count in counts.items():
        trimmed = bitstring[-qubits:]
        parity = (-1) ** trimmed.count("1")
        acc += parity * count
    return acc / total


def single_z_expectation(counts: dict[str, int], qubit: int) -> float:
    total = max(1, sum(int(value) for value in counts.values()))
    acc = 0.0
    for bitstring, count in counts.items():
        bit = int(bitstring[::-1][qubit])
        acc += (1.0 if bit == 0 else -1.0) * count
    return acc / total


def energy_from_counts(z_counts: dict[str, int], x_counts: dict[str, int]) -> dict[str, float]:
    z0 = single_z_expectation(z_counts, 0)
    z1 = single_z_expectation(z_counts, 1)
    z0z1 = parity_expectation(z_counts)
    x0x1 = parity_expectation(x_counts)
    energy = (
        H2_TOY_COEFFS["constant"]
        + H2_TOY_COEFFS["z0"] * z0
        + H2_TOY_COEFFS["z1"] * z1
        + H2_TOY_COEFFS["z0z1"] * z0z1
        + H2_TOY_COEFFS["x0x1"] * x0x1
    )
    return {"energy": energy, "z0": z0, "z1": z1, "z0z1": z0z1, "x0x1": x0x1}


def telemetry_from_energy(theta: float, energy: float, variance_proxy: float, latency_seconds: float) -> list[NodeTelemetry]:
    normalized_energy = max(0.0, min(1.0, (energy + 1.7) / 1.3))
    environment = EnvironmentVector(
        thermal=0.08 + variance_proxy * 0.20,
        electromagnetic=0.07 + abs(math.sin(theta)) * 0.10,
        voltage=0.06 + variance_proxy * 0.15,
        radiation=0.05 + normalized_energy * 0.08,
        latency=min(1.0, latency_seconds / 600.0),
    )
    telemetry = []
    for index in range(4):
        phase = theta + (index - 1.5) * 0.004
        vector = normalize_vector([math.cos(theta), math.sin(theta), 1.0 - normalized_energy])
        telemetry.append(
            NodeTelemetry(
                node_id=f"Q_NODE_{index}",
                raw_phase=phase,
                phase_velocity=0.05 + variance_proxy * 0.05,
                phase_acceleration=0.02 + variance_proxy * 0.04,
                bloch_vector=vector,
                signal_mu=0.24 + variance_proxy * 0.12,
                environment=environment,
                suspected_attack=False,
                crypto_valid=True,
                mission_priority=0.60,
            )
        )
    return telemetry


def run_vqe_bridge(
    backend_name: str = "ibm_marrakesh",
    shots: int = 512,
    seed: int = 2026,
    channel: str = "ibm_quantum_platform",
    reset_per_theta: bool = False,
) -> dict[str, object]:
    _, sampler_cls, generate_preset_pass_manager = require_runtime()
    _, backend = select_real_backend(channel=channel, backend_name=backend_name)
    print(f"[AEGIS VQE] Connected to IBM QPU: {backend.name}", flush=True)
    thetas = [0.20, 0.80, 1.40]
    circuits = []
    for theta in thetas:
        circuits.append(build_ansatz(theta, "z"))
        circuits.append(build_ansatz(theta, "x"))
    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuits = [pass_manager.run(circuit) for circuit in circuits]
    sampler = sampler_cls(mode=backend)
    started = time.perf_counter()
    job = sampler.run(isa_circuits, shots=shots)
    job_id = job.job_id() if hasattr(job, "job_id") else "unknown"
    print(f"[AEGIS VQE] Submitted job {job_id}: {len(thetas)} theta values x 2 bases. Waiting...", flush=True)
    result = job.result()
    elapsed = time.perf_counter() - started
    kernel = AegisContinuityKernel(seed=seed)
    records = []
    for index, theta in enumerate(thetas):
        if reset_per_theta:
            kernel = AegisContinuityKernel(seed=seed + index)
        z_counts = extract_sampler_counts([result[index * 2]])
        x_counts = extract_sampler_counts([result[index * 2 + 1]])
        metrics = energy_from_counts(z_counts, x_counts)
        variance_proxy = min(1.0, abs(metrics["x0x1"]) * 0.20 + abs(metrics["z0z1"]) * 0.10)
        cycle = kernel.execute_cycle(
            telemetry_from_energy(theta, metrics["energy"], variance_proxy, elapsed / len(thetas)),
            scenario=f"ibm_vqe_theta_{index}_{backend.name}",
        )
        records.append(
            {
                "theta": theta,
                "anchor_mode": "reset_per_theta_variational_setpoint" if reset_per_theta else "continuous_variational_track",
                "z_counts": z_counts,
                "x_counts": x_counts,
                **metrics,
                "q_conf": cycle.q_conf,
                "continuity_gate_passed": cycle.continuity_gate_passed,
                "governance_states": cycle.governance_states,
                "qom_compact_payload_hex": cycle.qom_compact_payload_hex,
                "merkle_root": cycle.merkle_root,
            }
        )
    best = min(records, key=lambda item: item["energy"])
    return {
        "source": "ibm_real_hardware_small_variational_vqe_style",
        "backend": backend.name,
        "job_id": job_id,
        "shots_per_circuit": shots,
        "circuits": len(circuits),
        "total_shots": shots * len(circuits),
        "anchor_mode": "reset_per_theta_variational_setpoint" if reset_per_theta else "continuous_variational_track",
        "round_trip_seconds": elapsed,
        "hamiltonian": H2_TOY_COEFFS,
        "best_theta": best["theta"],
        "best_energy": best["energy"],
        "mean_q_conf": sum(item["q_conf"] for item in records) / len(records),
        "continuity_gates_passed": sum(1 for item in records if item["continuity_gate_passed"]),
        "continuity_gates_total": len(records),
        "final_qom_compact_payload_bits": 176,
        "final_qom_compact_payload_hex": records[-1]["qom_compact_payload_hex"],
        "final_merkle_root": records[-1]["merkle_root"],
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Small VQE-style IBM bridge for AEGIS.")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--reset-per-theta", action="store_true", help="Treat each variational theta as a declared setpoint.")
    parser.add_argument("--output", type=Path, default=Path("ibm_vqe_bridge.json"))
    args = parser.parse_args()
    payload = run_vqe_bridge(args.backend, args.shots, args.seed, args.channel, reset_per_theta=args.reset_per_theta)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
