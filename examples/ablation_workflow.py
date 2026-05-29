from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_efficiency import is_accepted, summarize_efficiency, summary_to_dict


def apply_mode(record: dict, mode: str) -> dict:
    row = dict(record)
    ghz = float(row.get("ghz_population", row.get("raw_ghz_population", 1.0)))
    q_conf = float(row.get("q_conf", row.get("aegis_raw_q_conf", 1.0)))
    if mode == "raw_only":
        row["continuity_gate_passed"] = ghz >= 0.90
        row["q_conf"] = ghz
    elif mode == "no_anchor_gate":
        row["continuity_gate_passed"] = q_conf >= 0.88
    elif mode == "no_qom_lineage":
        row["qom_compact_payload_hex"] = ""
        row["merkle_root"] = ""
        row["continuity_gate_passed"] = False
    elif mode == "full_aegis":
        if "continuity_gate_passed" not in row and "aegis_raw_continuity_gate_passed" in row:
            row["continuity_gate_passed"] = bool(row["aegis_raw_continuity_gate_passed"])
    return row


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def target_values(record: dict) -> list[float]:
    values: list[float] = []
    for key in ("ghz_population", "raw_ghz_population", "mitigated_ghz_population", "selected_survival"):
        if key in record and record[key] is not None:
            values.append(float(record[key]))
    for row in record.get("records_summary") or []:
        if row.get("ghz_population") is not None:
            values.append(float(row["ghz_population"]))
    for row in record.get("arms_summary") or []:
        if row.get("survival") is not None:
            values.append(float(row["survival"]))
    return values


def governed_values(record: dict) -> list[float]:
    values: list[float] = []
    for key in ("q_conf", "aegis_raw_q_conf"):
        if key in record and record[key] is not None:
            values.append(float(record[key]))
    for row in record.get("records_summary") or []:
        if row.get("q_conf") is not None:
            values.append(float(row["q_conf"]))
    return values


def quality_breakdown(records: list[dict], mode_records: list[dict]) -> dict[str, object]:
    accepted = [row for row in mode_records if is_accepted(row)]
    raw_target_values = [value for row in records for value in target_values(row)]
    accepted_target_values = [value for row in accepted for value in target_values(row)]
    governed_scores = [value for row in accepted for value in governed_values(row)]
    return {
        "raw_target_quality_mean": mean(raw_target_values),
        "accepted_target_quality_mean": mean(accepted_target_values),
        "governed_quality_score_mean": mean(governed_scores),
        "quality_note": (
            "Do not compare raw_target_quality_mean to governed_quality_score_mean as one metric. "
            "Raw target quality is measured from GHZ/count data; governed quality is a stricter software score over accepted artifacts."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ablation workflow over sanitized validation artifacts.")
    parser.add_argument("--artifacts", type=Path, default=Path("docs/validation/raw_counts_sanitized"))
    parser.add_argument("--output", type=Path, default=Path("ablation_workflow.json"))
    args = parser.parse_args()
    records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.artifacts.glob("*.json"))]
    modes = ["raw_only", "no_anchor_gate", "no_qom_lineage", "full_aegis"]
    summaries = {}
    for mode in modes:
        mode_records = [apply_mode(row, mode) for row in records]
        summary = summary_to_dict(summarize_efficiency(mode_records))
        summary.pop("mean_accepted_quality", None)
        summary.update(quality_breakdown(records, mode_records))
        summaries[mode] = summary
    payload = {
        "source": "aegis_ablation_workflow",
        "modes": summaries,
        "claim_boundary": "Compares software gating/accounting modes over existing artifacts; not new QPU evidence. Quality fields are intentionally split to avoid comparing raw target fidelity against governed software scores.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
