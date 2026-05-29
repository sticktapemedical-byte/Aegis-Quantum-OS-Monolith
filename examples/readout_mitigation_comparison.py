from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.ibm_bridge import (
    build_measured_ghz_circuit,
    extract_sampler_counts,
    process_counts,
    require_qiskit_core,
    require_runtime,
    select_real_backend,
)


def build_readout_calibration_circuits() -> list[Any]:
    classical_register, quantum_circuit, quantum_register, _ = require_qiskit_core()
    circuits = []
    for qubit in range(4):
        for prepared_one in (False, True):
            qreg = quantum_register(4, "q")
            creg = classical_register(4, "meas")
            circuit = quantum_circuit(qreg, creg)
            if prepared_one:
                circuit.x(qreg[qubit])
            circuit.measure(qreg, creg)
            circuit.metadata = {"calibration_qubit": qubit, "prepared_one": prepared_one}
            circuits.append(circuit)
    return circuits


def bit_at(bitstring: str, qubit: int) -> str:
    return bitstring[::-1][qubit]


def estimate_assignment_matrix(calibration_counts: list[dict[str, int]]) -> list[list[list[float]]]:
    matrices = []
    for qubit in range(4):
        zero_counts = calibration_counts[qubit * 2]
        one_counts = calibration_counts[qubit * 2 + 1]
        zero_total = max(1, sum(zero_counts.values()))
        one_total = max(1, sum(one_counts.values()))
        p_obs_0_given_0 = sum(v for k, v in zero_counts.items() if bit_at(k, qubit) == "0") / zero_total
        p_obs_1_given_0 = 1.0 - p_obs_0_given_0
        p_obs_1_given_1 = sum(v for k, v in one_counts.items() if bit_at(k, qubit) == "1") / one_total
        p_obs_0_given_1 = 1.0 - p_obs_1_given_1
        matrices.append([[p_obs_0_given_0, p_obs_0_given_1], [p_obs_1_given_0, p_obs_1_given_1]])
    return matrices


def invert_2x2(matrix: list[list[float]]) -> list[list[float]]:
    a, b = matrix[0]
    c, d = matrix[1]
    det = (a * d) - (b * c)
    if abs(det) < 1e-9:
        return [[1.0, 0.0], [0.0, 1.0]]
    return [[d / det, -b / det], [-c / det, a / det]]


def apply_local_readout_mitigation(counts: dict[str, int], matrices: list[list[list[float]]]) -> dict[str, float]:
    basis_states = [format(index, "04b") for index in range(16)]
    distribution = {state: float(counts.get(state, 0)) for state in basis_states}
    for qubit, matrix in enumerate(matrices):
        inv = invert_2x2(matrix)
        updated = {state: 0.0 for state in basis_states}
        for state in basis_states:
            observed_bit = int(bit_at(state, qubit))
            for true_bit in (0, 1):
                true_state_bits = list(state)
                true_state_bits[3 - qubit] = str(true_bit)
                true_state = "".join(true_state_bits)
                updated[true_state] += inv[true_bit][observed_bit] * distribution[state]
        distribution = updated
    for key in distribution:
        distribution[key] = max(0.0, distribution[key])
    total = sum(distribution.values()) or 1.0
    return {key: value / total for key, value in distribution.items()}


def run_readout_mitigation_comparison(
    backend_name: str = "ibm_marrakesh",
    ghz_shots: int = 1024,
    calibration_shots: int = 256,
    seed: int = 2026,
    channel: str = "ibm_quantum_platform",
) -> dict[str, object]:
    _, sampler_cls, generate_preset_pass_manager = require_runtime()
    _, backend = select_real_backend(channel=channel, backend_name=backend_name)
    print(f"[AEGIS MITIGATION] Connected to IBM QPU: {backend.name}", flush=True)
    circuits = [build_measured_ghz_circuit()] + build_readout_calibration_circuits()
    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuits = [pass_manager.run(circuit) for circuit in circuits]
    sampler = sampler_cls(mode=backend)
    started = time.perf_counter()
    pubs = [(isa_circuits[0], None, ghz_shots)] + [(circuit, None, calibration_shots) for circuit in isa_circuits[1:]]
    job = sampler.run(pubs)
    job_id = job.job_id() if hasattr(job, "job_id") else "unknown"
    print(f"[AEGIS MITIGATION] Submitted job {job_id}: GHZ + 8 calibration circuits. Waiting...", flush=True)
    result = job.result()
    elapsed = time.perf_counter() - started
    ghz_counts = extract_sampler_counts([result[0]])
    calibration_counts = [extract_sampler_counts([result[index]]) for index in range(1, 9)]
    matrices = estimate_assignment_matrix(calibration_counts)
    mitigated_distribution = apply_local_readout_mitigation(ghz_counts, matrices)
    raw_payload = process_counts(
        ghz_counts,
        shots=ghz_shots,
        seed=seed,
        backend_name=backend.name,
        elapsed_seconds=elapsed,
        source="ibm_real_hardware_raw_ghz_for_mitigation",
    )
    raw_ghz_population = raw_payload["ghz_population"]
    mitigated_ghz_population = mitigated_distribution.get("0000", 0.0) + mitigated_distribution.get("1111", 0.0)
    improvement = mitigated_ghz_population - raw_ghz_population
    return {
        "source": "ibm_real_hardware_readout_mitigation_comparison",
        "backend": backend.name,
        "job_id": job_id,
        "ghz_shots": ghz_shots,
        "calibration_shots_per_circuit": calibration_shots,
        "calibration_circuits": 8,
        "total_shots": ghz_shots + (8 * calibration_shots),
        "round_trip_seconds": elapsed,
        "raw_counts": ghz_counts,
        "raw_ghz_population": raw_ghz_population,
        "raw_error_rate": raw_payload["raw_error_rate"],
        "mitigated_ghz_population": mitigated_ghz_population,
        "mitigated_error_rate": 1.0 - mitigated_ghz_population,
        "mitigation_delta": improvement,
        "assignment_matrices": matrices,
        "aegis_raw_q_conf": raw_payload["q_conf"],
        "aegis_raw_continuity_gate_passed": raw_payload["continuity_gate_passed"],
        "aegis_raw_governance_states": raw_payload["governance_states"],
        "qom_compact_payload_bits": raw_payload["qom_compact_payload_bits"],
        "qom_compact_payload_hex": raw_payload["qom_compact_payload_hex"],
        "merkle_root": raw_payload["merkle_root"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic local readout mitigation comparison for AEGIS IBM bridge.")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--ghz-shots", type=int, default=1024)
    parser.add_argument("--calibration-shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("ibm_readout_mitigation_comparison.json"))
    args = parser.parse_args()
    payload = run_readout_mitigation_comparison(
        backend_name=args.backend,
        ghz_shots=args.ghz_shots,
        calibration_shots=args.calibration_shots,
        seed=args.seed,
        channel=args.channel,
    )
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
