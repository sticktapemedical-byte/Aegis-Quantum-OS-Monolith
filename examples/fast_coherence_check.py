from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_kernel import AegisContinuityKernel, EnvironmentVector, NodeTelemetry, normalize_vector
from examples.ibm_bridge import extract_sampler_counts, require_runtime, select_real_backend


def require_qiskit():
    try:
        from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    except ImportError as exc:
        raise SystemExit("Install optional Qiskit packages with: python -m pip install -r requirements-qiskit.txt") from exc
    return ClassicalRegister, QuantumCircuit, QuantumRegister


def build_phase_rotation_circuit(phase_radians: float = math.pi / 2) -> Any:
    classical_register, quantum_circuit, quantum_register = require_qiskit()
    qreg = quantum_register(1, "q")
    creg = classical_register(1, "meas")
    circuit = quantum_circuit(qreg, creg)
    circuit.h(qreg[0])
    circuit.rz(phase_radians, qreg[0])
    circuit.h(qreg[0])
    circuit.measure(qreg[0], creg[0])
    return circuit


def telemetry_from_single_qubit_counts(
    counts: dict[str, int],
    shots: int,
    latency_seconds: float,
    seed: int,
) -> tuple[list[NodeTelemetry], dict[str, float]]:
    rng = random.Random(seed)
    total = max(1, sum(int(value) for value in counts.values()))
    one_population = int(counts.get("1", 0)) / total
    zero_population = int(counts.get("0", 0)) / total
    phase_balance_error = min(1.0, abs(one_population - 0.5) * 2.0)
    phase_estimate = 2.0 * math.asin(math.sqrt(max(0.0, min(1.0, one_population))))
    environment = EnvironmentVector(
        thermal=0.08 + phase_balance_error * 0.16,
        electromagnetic=0.08 + phase_balance_error * 0.22,
        voltage=0.06 + phase_balance_error * 0.12,
        radiation=0.05 + phase_balance_error * 0.18,
        latency=min(1.0, latency_seconds / 600.0),
    )
    telemetry = []
    for index in range(4):
        jitter = rng.uniform(-0.006, 0.006)
        phase = phase_estimate + jitter
        vector = normalize_vector(
            [
                math.cos(phase),
                math.sin(phase),
                zero_population - one_population,
            ]
        )
        telemetry.append(
            NodeTelemetry(
                node_id=f"Q_NODE_{index}",
                raw_phase=phase,
                phase_velocity=0.04 + phase_balance_error * 0.08,
                phase_acceleration=rng.uniform(-0.03, 0.03) + phase_balance_error * 0.04,
                bloch_vector=vector,
                signal_mu=0.22 + phase_balance_error * 0.18,
                environment=environment,
                suspected_attack=False,
                crypto_valid=True,
                mission_priority=0.55,
            )
        )
    return telemetry, {
        "zero_population": zero_population,
        "one_population": one_population,
        "phase_balance_error": phase_balance_error,
        "phase_estimate_radians": phase_estimate,
    }


def run_fast_coherence_pass(
    backend_name: str = "ibm_marrakesh",
    shots: int = 256,
    seed: int = 2026,
    channel: str = "ibm_quantum_platform",
) -> dict[str, object]:
    _, sampler_cls, generate_preset_pass_manager = require_runtime()
    _, backend = select_real_backend(channel=channel, backend_name=backend_name)
    print(f"[AEGIS FAST COHERENCE] Connected to IBM QPU: {backend.name}", flush=True)
    circuit = build_phase_rotation_circuit()
    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pass_manager.run(circuit)
    sampler = sampler_cls(mode=backend)
    started = time.perf_counter()
    job = sampler.run([isa_circuit], shots=shots)
    job_id = job.job_id() if hasattr(job, "job_id") else "unknown"
    print(f"[AEGIS FAST COHERENCE] Submitted job {job_id} with {shots} shots. Waiting for result...", flush=True)
    result = job.result()
    elapsed = time.perf_counter() - started
    counts = extract_sampler_counts(result)
    telemetry, phase_metrics = telemetry_from_single_qubit_counts(counts, shots, elapsed, seed)
    kernel = AegisContinuityKernel(seed=seed)
    cycle = kernel.execute_cycle(telemetry, scenario=f"ibm_fast_coherence_{backend.name}")
    return {
        "source": "ibm_real_hardware_fast_single_qubit",
        "backend": backend.name,
        "job_id": job_id,
        "shots": shots,
        "counts": counts,
        "total_counts": sum(int(value) for value in counts.values()),
        "round_trip_seconds": elapsed,
        **phase_metrics,
        "q_conf": cycle.q_conf,
        "trust_index": cycle.trust_index,
        "continuity_gate_passed": cycle.continuity_gate_passed,
        "governance_states": cycle.governance_states,
        "qom_compact_payload_bits": cycle.qom_compact_payload_bits,
        "qom_compact_payload_hex": cycle.qom_compact_payload_hex,
        "merkle_root": cycle.merkle_root,
        "opte_policy_context_hash": cycle.opte_policy_context_hash,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fast single-qubit IBM coherence/readout pass for AEGIS.")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("ibm_fast_coherence_marrakesh.json"))
    args = parser.parse_args()
    payload = run_fast_coherence_pass(
        backend_name=args.backend,
        shots=args.shots,
        seed=args.seed,
        channel=args.channel,
    )
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
