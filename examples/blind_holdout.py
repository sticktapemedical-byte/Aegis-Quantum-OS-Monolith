from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_efficiency import summarize_efficiency, summary_to_dict


def stable_bucket(name: str, holdout_fraction: float) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    value = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
    return "holdout" if value < holdout_fraction else "train"


def main() -> None:
    parser = argparse.ArgumentParser(description="Blind holdout split over sanitized validation artifacts.")
    parser.add_argument("--artifacts", type=Path, default=Path("docs/validation/raw_counts_sanitized"))
    parser.add_argument("--holdout-fraction", type=float, default=0.30)
    parser.add_argument("--output", type=Path, default=Path("blind_holdout.json"))
    args = parser.parse_args()
    train = []
    holdout = []
    for path in sorted(args.artifacts.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        record["_artifact_name"] = path.name
        (holdout if stable_bucket(path.name, args.holdout_fraction) == "holdout" else train).append(record)
    payload = {
        "source": "aegis_blind_holdout_workflow",
        "holdout_fraction": args.holdout_fraction,
        "train_count": len(train),
        "holdout_count": len(holdout),
        "train_artifacts": [row["_artifact_name"] for row in train],
        "holdout_artifacts": [row["_artifact_name"] for row in holdout],
        "train_efficiency": summary_to_dict(summarize_efficiency(train)),
        "holdout_efficiency": summary_to_dict(summarize_efficiency(holdout)),
        "claim_boundary": "Prevents post-hoc threshold tuning; not a new hardware result.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
