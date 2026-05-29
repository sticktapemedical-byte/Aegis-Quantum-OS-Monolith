from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_efficiency import summarize_efficiency, summary_to_dict


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Ablation workflow over sanitized validation artifacts.")
    parser.add_argument("--artifacts", type=Path, default=Path("docs/validation/raw_counts_sanitized"))
    parser.add_argument("--output", type=Path, default=Path("ablation_workflow.json"))
    args = parser.parse_args()
    records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.artifacts.glob("*.json"))]
    modes = ["raw_only", "no_anchor_gate", "no_qom_lineage", "full_aegis"]
    summaries = {}
    for mode in modes:
        summaries[mode] = summary_to_dict(summarize_efficiency(apply_mode(row, mode) for row in records))
    payload = {
        "source": "aegis_ablation_workflow",
        "modes": summaries,
        "claim_boundary": "Compares software gating/accounting modes over existing artifacts; not new QPU evidence.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
