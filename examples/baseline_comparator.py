from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_stats import mean, sample_std, wilson_interval


def load_artifacts(root: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(root.glob("*.json"))
    ]


def compare_baselines(artifacts: list[dict]) -> dict[str, object]:
    ghz = [item for item in artifacts if "ghz_population" in item]
    accepted = [
        item for item in ghz
        if item.get("qom_compact_payload_hex") and item.get("merkle_root")
    ]
    mitigated = [item for item in artifacts if "mitigated_ghz_population" in item]
    setpoints = [item for item in artifacts if "setpoint_validations_total" in item]
    total_setpoint_passes = sum(int(item["setpoint_validations_passed"]) for item in setpoints)
    total_setpoints = sum(int(item["setpoint_validations_total"]) for item in setpoints)
    setpoint_ci = wilson_interval(total_setpoint_passes, total_setpoints) if total_setpoints else None
    return {
        "raw_ghz_runs": len(ghz),
        "raw_ghz_mean": mean(item["ghz_population"] for item in ghz),
        "raw_ghz_std": sample_std(item["ghz_population"] for item in ghz),
        "aegis_governed_ghz_runs": len(accepted),
        "aegis_governed_ghz_mean": mean(item["ghz_population"] for item in accepted),
        "mitigation_runs": len(mitigated),
        "mitigation_mean_raw": mean(item["raw_ghz_population"] for item in mitigated),
        "mitigation_mean_mitigated": mean(item["mitigated_ghz_population"] for item in mitigated),
        "mitigation_mean_delta": mean(item["mitigation_delta"] for item in mitigated),
        "setpoint_passes": total_setpoint_passes,
        "setpoint_total": total_setpoints,
        "setpoint_pass_rate": total_setpoint_passes / total_setpoints if total_setpoints else 0.0,
        "setpoint_pass_wilson_95": {"low": setpoint_ci.low, "high": setpoint_ci.high} if setpoint_ci else None,
        "claim_boundary": "Classical comparison over returned counts; not a claim of physical noise suppression.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare raw, AEGIS-governed, mitigated, and setpoint validation artifacts.")
    parser.add_argument("--artifacts", type=Path, default=Path("docs/validation/raw_counts_sanitized"))
    parser.add_argument("--output", type=Path, default=Path("docs/validation/baseline_comparison.json"))
    args = parser.parse_args()
    payload = compare_baselines(load_artifacts(args.artifacts))
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
