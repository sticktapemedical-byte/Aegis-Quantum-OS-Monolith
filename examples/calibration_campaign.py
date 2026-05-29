from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def synthetic_rb(seed: int, lengths: list[int], shots: int) -> dict[str, object]:
    rng = random.Random(seed)
    epc = 0.006 + rng.random() * 0.003
    rows = []
    for length in lengths:
        survival = 0.5 + 0.5 * ((1.0 - epc) ** length)
        rows.append({"length": length, "shots": shots, "survival": survival, "successes": int(shots * survival)})
    return {"type": "randomized_benchmarking_proxy", "epc_estimate": epc, "records": rows}


def synthetic_t1_t2(seed: int, delays_us: list[float], shots: int) -> dict[str, object]:
    rng = random.Random(seed)
    t1 = 95.0 + rng.random() * 20.0
    t2 = 70.0 + rng.random() * 15.0
    t1_rows = [{"delay_us": d, "p1": math.exp(-d / t1), "shots": shots} for d in delays_us]
    t2_rows = [{"delay_us": d, "contrast": math.exp(-d / t2), "shots": shots} for d in delays_us]
    return {"type": "t1_t2_ramsey_proxy", "t1_us": t1, "t2_us": t2, "t1_records": t1_rows, "t2_records": t2_rows}


def synthetic_tomography(seed: int, shots: int) -> dict[str, object]:
    rng = random.Random(seed)
    fidelity = 0.92 + rng.random() * 0.05
    return {
        "type": "tomography_proxy",
        "shots_per_basis": shots,
        "bases": ["XX", "YY", "ZZ"],
        "fidelity_proxy": fidelity,
        "trace_distance_proxy": max(0.0, 1.0 - fidelity),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="RB/T1/T2/tomography calibration campaign harness.")
    parser.add_argument("--real", action="store_true", help="Reserved for future calibrated hardware campaign; currently records unsupported.")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--lengths", default="1,2,4,8,16,32")
    parser.add_argument("--delays-us", default="0,10,25,50,100")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("calibration_campaign.json"))
    args = parser.parse_args()
    lengths = [int(item.strip()) for item in args.lengths.split(",") if item.strip()]
    delays = [float(item.strip()) for item in args.delays_us.split(",") if item.strip()]
    if args.real:
        payload = {
            "source": "aegis_calibration_campaign",
            "real": True,
            "backend": args.backend,
            "status": "real_calibration_campaign_not_queued_by_default",
            "reason": "RB/T1/T2/tomography requires a dedicated shot budget and backend-calibration plan.",
        }
    else:
        payload = {
            "source": "aegis_calibration_campaign",
            "real": False,
            "backend": args.backend,
            "rb": synthetic_rb(args.seed, lengths, args.shots),
            "t1_t2": synthetic_t1_t2(args.seed + 1, delays, args.shots),
            "tomography": synthetic_tomography(args.seed + 2, args.shots),
            "status": "synthetic_campaign_complete",
        }
    payload["claim_boundary"] = "Calibration harness for correlation studies; synthetic unless a dedicated real campaign is explicitly implemented and queued."
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
