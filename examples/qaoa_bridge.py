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
from examples.ibm_bridge import extract_sampler_counts, require_qiskit_core, require_runtime, select_real_backend


EDGES = [(0, 1), (1, 2), (0, 2)]


def build_qaoa_circuit(gamma: float, beta: float) -> Any:
    classical_register, quantum_circuit, quantum_register, _ = require_qiskit_core()
    qreg = quantum_register(3, "q")
    creg = classical_register(3, "meas")
    circuit = quantum_circuit(qreg, creg)
    for q in range(3):
        circuit.h(qreg[q])
    for a, b in EDGES:
        circuit.cx(qreg[a], qreg[b])
        circuit.rz(2.0 * gamma, qreg[b])
        circuit.cx(qreg[a], qreg[b])
    for q in range(3):
        circuit.rx(2.0 * beta, qreg[q])
    circuit.measure(qreg, creg)
    return circuit


def maxcut_value(bitstring: str) -> int:
    bits = bitstring[-3:]
    return sum(1 for a, b in EDGES if bits[::-1][a] != bits[::-1][b])


def score_counts(counts: dict[str, int]) -> dict[str, float]:
    total = max(1, sum(counts.values()))
    expected_cut = sum(maxcut_value(bitstring) * count for bitstring, count in counts.items()) / total
    best_state_population = sum(count for bitstring, count in counts.items() if maxcut_value(bitstring) == 2) / total
    return {"expected_cut": expected_cut, "best_state_population": best_state_population}


def aegis_govern(beta: float, gamma: float, score: dict[str, float], latency: float) -> dict[str, object]:
    kernel = AegisContinuityKernel()
    quality = float(score["best_state_population"])
    env = EnvironmentVector(
        thermal=0.08 + (1.0 - quality) * 0.10,
        electromagnetic=0.06 + abs(math.sin(gamma)) * 0.08,
        voltage=0.06 + abs(math.sin(beta)) * 0.08,
        radiation=0.05 + (1.0 - quality) * 0.06,
        latency=min(1.0, latency / 600.0),
    )
    telemetry = []
    phase = math.atan2(math.sin(beta + gamma), math.cos(beta + gamma))
    for idx in range(4):
        telemetry.append(
            NodeTelemetry(
                node_id=f"Q_NODE_{idx}",
                raw_phase=phase + idx * 0.003,
                phase_velocity=0.04,
                phase_acceleration=0.01,
                bloch_vector=normalize_vector([quality, math.sin(beta), math.cos(gamma)]),
                signal_mu=0.20 + (1.0 - quality) * 0.10,
                environment=env,
                suspected_attack=False,
                crypto_valid=True,
                mission_priority=0.65,
            )
        )
    result = kernel.execute_cycle(telemetry, scenario="qaoa_bridge")
    return {
        "q_conf": result.q_conf,
        "continuity_gate_passed": result.continuity_gate_passed,
        "governance_states": result.governance_states,
        "qom_compact_payload_bits": result.qom_compact_payload_bits,
        "qom_compact_payload_hex": result.qom_compact_payload_hex,
        "merkle_root": result.merkle_root,
    }


def synthetic_counts(gamma: float, beta: float, shots: int, seed: int) -> dict[str, int]:
    rng = random.Random(seed + int(gamma * 1000) + int(beta * 1000))
    base = 0.45 + 0.25 * math.sin(gamma + beta)
    counts = {format(i, "03b"): 0 for i in range(8)}
    for _ in range(shots):
        if rng.random() < base:
            state = rng.choice(["001", "010", "101", "110"])
        else:
            state = rng.choice(list(counts))
        counts[state] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Small QAOA MaxCut bridge with AEGIS governance.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--grid", default="0.35:0.25,0.65:0.35,0.95:0.45,1.25:0.55")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("qaoa_bridge.json"))
    args = parser.parse_args()
    pairs = [tuple(float(x) for x in item.split(":")) for item in args.grid.split(",") if item.strip()]
    records = []
    if args.real:
        _, sampler_cls, generate_preset_pass_manager = require_runtime()
        _, backend = select_real_backend(channel=args.channel, backend_name=args.backend)
        sampler = sampler_cls(mode=backend)
        for index, (gamma, beta) in enumerate(pairs):
            circuit = build_qaoa_circuit(gamma, beta)
            pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
            isa = pm.run(circuit)
            start = time.perf_counter()
            job = sampler.run([isa], shots=args.shots)
            result = job.result()
            latency = time.perf_counter() - start
            counts = extract_sampler_counts(result)
            score = score_counts(counts)
            records.append({"gamma": gamma, "beta": beta, "backend": backend.name, "job_id": job.job_id(), "shots": args.shots, "counts": counts, **score, **aegis_govern(beta, gamma, score, latency), "round_trip_seconds": latency})
    else:
        for index, (gamma, beta) in enumerate(pairs):
            counts = synthetic_counts(gamma, beta, args.shots, args.seed + index)
            score = score_counts(counts)
            records.append({"gamma": gamma, "beta": beta, "backend": "synthetic_qaoa", "shots": args.shots, "counts": counts, **score, **aegis_govern(beta, gamma, score, 0.0)})
    best = max(records, key=lambda row: float(row["expected_cut"])) if records else None
    payload = {
        "source": "aegis_qaoa_bridge",
        "real": args.real,
        "backend": args.backend,
        "shots_per_point": args.shots,
        "records": records,
        "best": best,
        "claim_boundary": "Small QAOA workload ingestion and governance; not a quantum advantage or optimizer-performance claim.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
