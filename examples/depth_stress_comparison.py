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

from examples.ibm_bridge import extract_sampler_counts, process_counts, require_qiskit_core, require_runtime, select_real_backend


def build_depth_stress_ghz(depth_layers: int) -> Any:
    classical_register, quantum_circuit, quantum_register, _ = require_qiskit_core()
    qreg = quantum_register(4, "q")
    creg = classical_register(4, "meas")
    circuit = quantum_circuit(qreg, creg)
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


def run_depth_stress(
    backend_name: str = "ibm_marrakesh",
    shots: int = 512,
    seed: int = 2026,
    channel: str = "ibm_quantum_platform",
) -> dict[str, object]:
    _, sampler_cls, generate_preset_pass_manager = require_runtime()
    _, backend = select_real_backend(channel=channel, backend_name=backend_name)
    print(f"[AEGIS DEPTH STRESS] Connected to IBM QPU: {backend.name}", flush=True)
    depths = [2, 4, 6]
    circuits = [build_depth_stress_ghz(depth) for depth in depths]
    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuits = [pass_manager.run(circuit) for circuit in circuits]
    sampler = sampler_cls(mode=backend)
    started = time.perf_counter()
    job = sampler.run(isa_circuits, shots=shots)
    job_id = job.job_id() if hasattr(job, "job_id") else "unknown"
    print(f"[AEGIS DEPTH STRESS] Submitted job {job_id}: depths {depths} x {shots} shots. Waiting...", flush=True)
    result = job.result()
    elapsed = time.perf_counter() - started
    records = []
    for index, depth in enumerate(depths):
        counts = extract_sampler_counts([result[index]])
        payload = process_counts(
            counts,
            shots=shots,
            seed=seed + index,
            backend_name=backend.name,
            elapsed_seconds=elapsed / len(depths),
            source=f"ibm_real_hardware_depth_stress_{depth}",
        )
        records.append({"depth_layers": depth, **payload})
    return {
        "source": "ibm_real_hardware_cross_depth_noise_stress",
        "backend": backend.name,
        "job_id": job_id,
        "shots_per_depth": shots,
        "depths": depths,
        "total_shots": shots * len(depths),
        "round_trip_seconds": elapsed,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-depth GHZ noise stress comparison for AEGIS IBM bridge.")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("ibm_depth_stress_comparison.json"))
    args = parser.parse_args()
    payload = run_depth_stress(args.backend, args.shots, args.seed, args.channel)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
