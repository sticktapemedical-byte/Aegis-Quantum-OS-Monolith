from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.ibm_bridge import process_counts, require_qiskit_core, require_runtime, select_real_backend


def synthetic_dd_arm(sequence: str, delay_us: float) -> dict[str, object]:
    base_t = {"none": 45.0, "xx": 58.0, "xy4": 66.0, "cpmg": 61.0}.get(sequence, 45.0)
    survival = max(0.0, min(0.999, math.exp(-delay_us / base_t)))
    shots = 512
    good = int(round(shots * survival))
    counts = {"0": good, "1": shots - good}
    return {
        "sequence": sequence,
        "delay_us": delay_us,
        "shots": shots,
        "survival": survival,
        "counts": counts,
        "status": "synthetic_dd_model",
    }


def build_idle_echo_circuit(sequence: str, delay_us: float):
    _, quantum_circuit, _, _ = require_qiskit_core()
    circuit = quantum_circuit(1, 1)
    circuit.h(0)
    half_delay = max(0.0, delay_us / 2.0)
    if sequence == "none":
        circuit.delay(delay_us, 0, unit="us")
    elif sequence == "xx":
        circuit.delay(half_delay, 0, unit="us")
        circuit.x(0)
        circuit.delay(half_delay, 0, unit="us")
        circuit.x(0)
    elif sequence in ("xy4", "cpmg"):
        quarter = max(0.0, delay_us / 4.0)
        for gate in ("x", "y", "x", "y"):
            circuit.delay(quarter, 0, unit="us")
            getattr(circuit, gate)(0)
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def run_real_dd_arm(sequence: str, delay_us: float, backend_name: str, shots: int, channel: str) -> dict[str, object]:
    _, sampler_cls, generate_preset_pass_manager = require_runtime()
    _, backend = select_real_backend(channel=channel, backend_name=backend_name)
    circuit = build_idle_echo_circuit(sequence, delay_us)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa = pm.run(circuit)
    sampler = sampler_cls(mode=backend)
    job = sampler.run([isa], shots=shots)
    result = job.result()
    from examples.ibm_bridge import extract_sampler_counts
    counts = extract_sampler_counts(result)
    good = int(counts.get("0", 0))
    payload = process_counts(
        {"0000": good, "1111": max(0, shots - good)},
        shots=shots,
        seed=2026,
        backend_name=backend.name,
        elapsed_seconds=0.0,
        source=f"ibm_real_dd_{sequence}",
    )
    return {
        "sequence": sequence,
        "delay_us": delay_us,
        "backend": backend.name,
        "job_id": job.job_id() if hasattr(job, "job_id") else "unknown",
        "shots": shots,
        "counts": counts,
        "survival": good / max(1, sum(counts.values())),
        "aegis": payload,
        "status": "real_job_complete",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamical-decoupling insertion harness for idle-window workloads.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--delay-us", type=float, default=50.0)
    parser.add_argument("--sequences", default="none,xx,xy4,cpmg")
    parser.add_argument("--output", type=Path, default=Path("dynamical_decoupling_insertion.json"))
    args = parser.parse_args()
    arms = []
    for sequence in [item.strip() for item in args.sequences.split(",") if item.strip()]:
        if args.real:
            try:
                arms.append(run_real_dd_arm(sequence, args.delay_us, args.backend, args.shots, args.channel))
            except Exception as exc:
                arms.append({"sequence": sequence, "status": "unsupported_or_failed", "error": str(exc)})
        else:
            arms.append(synthetic_dd_arm(sequence, args.delay_us))
    selected = max(arms, key=lambda item: float(item.get("survival", 0.0)))
    payload = {
        "source": "aegis_dynamical_decoupling_insertion",
        "real": args.real,
        "backend": args.backend,
        "arms": arms,
        "selected_sequence": selected.get("sequence"),
        "claim_boundary": "Inserts simple idle echo/DD-style gates where supported; does not claim intrinsic coherence extension.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
