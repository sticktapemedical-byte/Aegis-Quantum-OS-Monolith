from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_stats import mean, sample_std, wilson_interval
from examples.dynamical_decoupling_insertion import run_real_dd_arm, synthetic_dd_arm


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries = []
    for sequence in sorted({str(row.get("sequence")) for row in rows}):
        seq_rows = [row for row in rows if row.get("sequence") == sequence and row.get("survival") is not None]
        if not seq_rows:
            continue
        total_shots = sum(int(row.get("shots") or 0) for row in seq_rows)
        successes = sum(round(float(row["survival"]) * int(row.get("shots") or 0)) for row in seq_rows)
        ci = wilson_interval(successes, total_shots) if total_shots else None
        survival_values = [float(row["survival"]) for row in seq_rows]
        summaries.append(
            {
                "sequence": sequence,
                "runs": len(seq_rows),
                "total_shots": total_shots,
                "mean_survival": mean(survival_values),
                "std_survival": sample_std(survival_values),
                "wilson_95": {"low": ci.low, "high": ci.high} if ci else None,
            }
        )
    summaries.sort(key=lambda item: float(item["mean_survival"]), reverse=True)
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Repeated DD-style idle echo campaign over delay values.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--delays-us", default="25,50,100")
    parser.add_argument("--sequences", default="none,xx,xy4,cpmg")
    parser.add_argument("--output", type=Path, default=Path("dd_repeat_campaign.json"))
    args = parser.parse_args()

    delays = [float(item.strip()) for item in args.delays_us.split(",") if item.strip()]
    sequences = [item.strip() for item in args.sequences.split(",") if item.strip()]
    rows = []
    for repeat in range(args.repeats):
        for delay_us in delays:
            for sequence in sequences:
                try:
                    if args.real:
                        row = run_real_dd_arm(sequence, delay_us, args.backend, args.shots, args.channel)
                    else:
                        row = synthetic_dd_arm(sequence, delay_us)
                    row["repeat"] = repeat
                    row["delay_us"] = delay_us
                except Exception as exc:
                    row = {
                        "repeat": repeat,
                        "delay_us": delay_us,
                        "sequence": sequence,
                        "status": "failed",
                        "error": str(exc),
                    }
                rows.append(row)
    summary = summarize(rows)
    payload = {
        "source": "aegis_dd_repeat_campaign",
        "real": args.real,
        "backend": args.backend,
        "repeats": args.repeats,
        "shots_per_arm": args.shots,
        "delays_us": delays,
        "sequences": sequences,
        "records": rows,
        "summary": summary,
        "selected_sequence": summary[0]["sequence"] if summary else None,
        "claim_boundary": "Repeated idle echo/DD-style comparison over returned outputs; not calibrated pulse-level DD and not intrinsic coherence improvement.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
