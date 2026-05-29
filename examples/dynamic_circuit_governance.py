from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_dynamic_circuit():
    from qiskit import QuantumCircuit
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.measure(0, 0)
    with circuit.if_test((0, 1)):
        circuit.x(1)
    circuit.measure(1, 1)
    return circuit


def synthetic_result(shots: int) -> dict[str, object]:
    return {
        "status": "synthetic_dynamic_circuit",
        "shots": shots,
        "counts": {"11": int(shots * 0.49), "00": int(shots * 0.49), "10": shots - int(shots * 0.98)},
        "governance_decision": "ACCEPT_DYNAMIC_FEED_FORWARD_PATTERN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamic-circuit governance harness.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--output", type=Path, default=Path("dynamic_circuit_governance.json"))
    args = parser.parse_args()
    if not args.real:
        payload = {"source": "aegis_dynamic_circuit_governance", "real": False, **synthetic_result(args.shots)}
    else:
        try:
            from examples.ibm_bridge import extract_sampler_counts, require_runtime, select_real_backend
            _, sampler_cls, generate_preset_pass_manager = require_runtime()
            _, backend = select_real_backend(args.channel, args.backend)
            circuit = build_dynamic_circuit()
            isa = generate_preset_pass_manager(optimization_level=1, backend=backend).run(circuit)
            sampler = sampler_cls(mode=backend)
            job = sampler.run([isa], shots=args.shots)
            counts = extract_sampler_counts(job.result())
            payload = {
                "source": "aegis_dynamic_circuit_governance",
                "real": True,
                "backend": backend.name,
                "job_id": job.job_id() if hasattr(job, "job_id") else "unknown",
                "shots": args.shots,
                "counts": counts,
                "status": "real_job_complete",
            }
        except Exception as exc:
            payload = {
                "source": "aegis_dynamic_circuit_governance",
                "real": True,
                "backend": args.backend,
                "status": "unsupported_or_failed",
                "error": str(exc),
            }
    payload["claim_boundary"] = "Uses hardware-supported dynamic circuits only if available; otherwise reports unsupported without claiming real-time control."
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
