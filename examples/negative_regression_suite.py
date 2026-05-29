from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.ibm_bridge import run_fake_backend_once, run_real_hardware_once


def main() -> None:
    parser = argparse.ArgumentParser(description="Negative-result regression suite across backends and stressors.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backends", default="ibm_marrakesh,ibm_kingston,ibm_fez")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=128)
    parser.add_argument("--delays-ms", default="0,2,10")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("negative_regression_suite.json"))
    args = parser.parse_args()
    backends = [item.strip() for item in args.backends.split(",") if item.strip()]
    delays = [float(item.strip()) for item in args.delays_ms.split(",") if item.strip()]
    rows = []
    index = 0
    for backend in backends:
        for delay in delays:
            try:
                if args.real:
                    row = run_real_hardware_once(args.shots, args.seed + index, args.channel, backend_name=backend, delay_ms=delay)
                else:
                    row = run_fake_backend_once(args.shots, args.seed + index, delay_ms=delay)
                    row["requested_backend"] = backend
                row["stress_profile"] = "delay_ms"
                row["requested_delay_ms"] = delay
                row["expected_negative_allowed"] = True
            except Exception as exc:
                row = {
                    "backend": backend,
                    "requested_delay_ms": delay,
                    "status": "blocked_or_failed",
                    "error": str(exc),
                    "expected_negative_allowed": True,
                }
            rows.append(row)
            index += 1
    payload = {
        "source": "aegis_negative_regression_suite",
        "real": args.real,
        "backends": backends,
        "shots": args.shots,
        "delays_ms": delays,
        "records": rows,
        "claim_boundary": "Preserves blocked, failed, and low-quality outputs as regression evidence; not a performance claim.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
