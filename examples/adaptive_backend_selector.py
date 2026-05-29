from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.ibm_bridge import run_fake_backend_once, run_real_hardware_once


def score_backend(record: dict, alpha: float = 0.55, beta: float = 0.30, gamma: float = 0.10, delta: float = 0.05) -> float:
    fidelity = float(record["ghz_population"])
    q_conf = float(record["q_conf"])
    latency = min(1.0, float(record["round_trip_seconds"]) / 600.0)
    risk = float(record["raw_error_rate"])
    return (alpha * fidelity) + (beta * q_conf) - (gamma * latency) - (delta * risk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe IBM backends and select a committed backend using AEGIS score.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backends", default="ibm_marrakesh,ibm_kingston,ibm_fez")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--probe-shots", type=int, default=256)
    parser.add_argument("--commit-shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("adaptive_backend_selector.json"))
    args = parser.parse_args()
    backends = [item.strip() for item in args.backends.split(",") if item.strip()]
    probes = []
    for index, backend in enumerate(backends):
        try:
            if args.real:
                probe = run_real_hardware_once(args.probe_shots, args.seed + index, args.channel, backend_name=backend)
            else:
                probe = run_fake_backend_once(args.probe_shots, args.seed + index)
                probe["requested_backend"] = backend
            probe["selector_score"] = score_backend(probe)
        except Exception as exc:
            probe = {
                "requested_backend": backend,
                "backend": backend,
                "probe_failed": True,
                "error": str(exc),
                "selector_score": float("-inf"),
            }
        probes.append(probe)
    successful_probes = [probe for probe in probes if not probe.get("probe_failed")]
    if not successful_probes:
        raise SystemExit("All probe backends failed; no committed workload submitted.")
    selected = max(successful_probes, key=lambda item: item["selector_score"])
    selected_backend = selected.get("backend") if args.real else selected.get("requested_backend", selected.get("backend"))
    if args.real:
        committed = run_real_hardware_once(args.commit_shots, args.seed + 99, args.channel, backend_name=selected_backend)
    else:
        committed = run_fake_backend_once(args.commit_shots, args.seed + 99)
        committed["requested_backend"] = selected_backend
    payload = {
        "source": "aegis_adaptive_backend_selector",
        "real": args.real,
        "candidate_backends": backends,
        "probe_shots": args.probe_shots,
        "commit_shots": args.commit_shots,
        "probes": probes,
        "selected_backend": selected_backend,
        "selected_score": selected["selector_score"],
        "committed_run": committed,
        "claim_boundary": "Adaptive backend selection over cloud-QPU output quality; not physical hardware modification.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
