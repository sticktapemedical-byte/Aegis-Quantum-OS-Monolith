from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_efficiency import summarize_efficiency, summary_to_dict
from aegis_stats import mean, resource_cost_per_accepted_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Resource-efficiency summary for sanitized AEGIS validation artifacts.")
    parser.add_argument("--artifacts", type=Path, default=Path("docs/validation/raw_counts_sanitized"))
    parser.add_argument("--output", type=Path, default=Path("docs/validation/efficiency_summary.json"))
    args = parser.parse_args()
    artifacts = [json.loads(path.read_text(encoding="utf-8")) for path in args.artifacts.glob("*.json")]
    total_shots = sum(int(item.get("shots") or 0) for item in artifacts)
    accepted = [
        item for item in artifacts
        if item.get("qom_compact_payload_hex")
        and item.get("merkle_root")
        and (item.get("ghz_population", 1.0) >= 0.90 or item.get("setpoint_validations_passed", 0) > 0)
    ]
    payload = {
        "source": "aegis_efficiency_summary",
        "artifact_count": len(artifacts),
        "total_tracked_shots": total_shots,
        "accepted_artifact_count": len(accepted),
        "shots_per_accepted_artifact": resource_cost_per_accepted_result(total_shots, len(accepted)),
        "mean_accepted_ghz": mean(item["ghz_population"] for item in accepted if "ghz_population" in item),
        "standard_efficiency": summary_to_dict(summarize_efficiency(artifacts)),
        "claim_boundary": "Resource accounting over validation artifacts; not refrigerator power measurement.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
