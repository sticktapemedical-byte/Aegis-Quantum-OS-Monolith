from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.ibm_bridge import run_fake_backend_once, run_real_hardware_once, select_real_backend


def synthetic_layout_candidates() -> list[dict[str, object]]:
    return [
        {"layout": [0, 1, 2, 3], "mean_cx_error": 0.012, "mean_readout_error": 0.018, "chain_length": 3, "score": 0.970},
        {"layout": [4, 5, 6, 7], "mean_cx_error": 0.018, "mean_readout_error": 0.016, "chain_length": 3, "score": 0.958},
        {"layout": [10, 11, 12, 13], "mean_cx_error": 0.022, "mean_readout_error": 0.021, "chain_length": 3, "score": 0.943},
    ]


def backend_layout_candidates(backend) -> list[dict[str, object]]:
    try:
        target = backend.target
        qubits = list(range(min(backend.num_qubits, 24)))
        candidates = []
        for start in range(0, max(1, len(qubits) - 3), 4):
            layout = qubits[start:start + 4]
            if len(layout) < 4:
                continue
            cx_errors = []
            readout_errors = []
            for qubit in layout:
                try:
                    readout_errors.append(float(target["measure"][(qubit,)].error or 0.02))
                except Exception:
                    readout_errors.append(0.02)
            for a, b in zip(layout, layout[1:]):
                try:
                    cx_errors.append(float(target["cx"][(a, b)].error or target["ecr"][(a, b)].error or 0.02))
                except Exception:
                    cx_errors.append(0.02)
            mean_cx = sum(cx_errors) / max(1, len(cx_errors))
            mean_ro = sum(readout_errors) / max(1, len(readout_errors))
            score = 1.0 - (0.65 * mean_cx) - (0.35 * mean_ro)
            candidates.append({"layout": layout, "mean_cx_error": mean_cx, "mean_readout_error": mean_ro, "chain_length": 3, "score": score})
        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:8] or synthetic_layout_candidates()
    except Exception:
        return synthetic_layout_candidates()


def main() -> None:
    parser = argparse.ArgumentParser(description="AEGIS adaptive layout selector.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--probe-shots", type=int, default=256)
    parser.add_argument("--commit-shots", type=int, default=1024)
    parser.add_argument("--output", type=Path, default=Path("adaptive_layout_selector.json"))
    args = parser.parse_args()
    if args.real:
        _, backend = select_real_backend(args.channel, args.backend)
        candidates = backend_layout_candidates(backend)
        committed = run_real_hardware_once(args.commit_shots, backend_name=args.backend, channel=args.channel)
    else:
        candidates = synthetic_layout_candidates()
        committed = run_fake_backend_once(args.commit_shots)
    payload = {
        "source": "aegis_adaptive_layout_selector",
        "real": args.real,
        "backend": args.backend,
        "candidate_layouts": candidates,
        "selected_layout": candidates[0],
        "committed_run": committed,
        "claim_boundary": "Selects a candidate qubit layout for later runs; does not claim intrinsic device improvement.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
