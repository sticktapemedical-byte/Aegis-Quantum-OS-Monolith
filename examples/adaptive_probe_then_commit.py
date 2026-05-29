from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.adaptive_backend_selector import score_backend
from examples.ibm_bridge import run_fake_backend_once, run_real_hardware_once


def probe_then_commit(real: bool, backends: list[str], probe_shots: int, commit_shots: int, channel: str) -> dict[str, object]:
    probes = []
    for index, backend in enumerate(backends):
        try:
            record = (
                run_real_hardware_once(shots=probe_shots, seed=2026 + index, channel=channel, backend_name=backend)
                if real else run_fake_backend_once(shots=probe_shots, seed=2026 + index)
            )
        except Exception as exc:
            record = {
                "requested_backend": backend,
                "backend": backend,
                "probe_failed": True,
                "error": str(exc),
                "selector_score": float("-inf"),
            }
            probes.append(record)
            continue
        record["requested_backend"] = backend
        record["selector_score"] = score_backend(record)
        probes.append(record)
    successful_probes = [probe for probe in probes if not probe.get("probe_failed")]
    if not successful_probes:
        raise SystemExit("All probe backends failed; no committed workload submitted.")
    selected = max(successful_probes, key=lambda item: item["selector_score"])
    selected_backend = str(selected["requested_backend"])
    committed = (
        run_real_hardware_once(shots=commit_shots, seed=2099, channel=channel, backend_name=selected_backend)
        if real else run_fake_backend_once(shots=commit_shots, seed=2099)
    )
    committed["requested_backend"] = selected_backend
    return {
        "source": "aegis_adaptive_probe_then_commit",
        "real": real,
        "candidate_backends": backends,
        "probe_shots": probe_shots,
        "commit_shots": commit_shots,
        "probes": probes,
        "selected_backend": selected_backend,
        "selected_score": selected["selector_score"],
        "committed_run": committed,
        "claim_boundary": "Probe results select a later committed workload; no claim of in-circuit QPU control.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AEGIS probe-then-commit adaptive backend controller.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backends", default="ibm_marrakesh,ibm_kingston,ibm_fez")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--probe-shots", type=int, default=256)
    parser.add_argument("--commit-shots", type=int, default=1024)
    parser.add_argument("--output", type=Path, default=Path("adaptive_probe_then_commit.json"))
    args = parser.parse_args()
    backends = [item.strip() for item in args.backends.split(",") if item.strip()]
    payload = probe_then_commit(args.real, backends, args.probe_shots, args.commit_shots, args.channel)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
