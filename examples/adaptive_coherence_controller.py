from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.delay_ramp import run_delay_ramp


def fit_effective_decay(delays_ms: list[float], survivals: list[float]) -> dict[str, float]:
    pairs = [(x, y) for x, y in zip(delays_ms, survivals) if x >= 0 and 0 < y < 1.0]
    if len(pairs) < 2:
        return {"t_eff_ms": 0.0, "slope": 0.0, "intercept": 0.0}
    xs = [p[0] for p in pairs]
    ys = [math.log(p[1]) for p in pairs]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs) or 1.0
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom
    intercept = ybar - slope * xbar
    t_eff = -1.0 / slope if slope < 0 else float("inf")
    return {"t_eff_ms": t_eff if math.isfinite(t_eff) else 999999.0, "slope": slope, "intercept": intercept}


def synthetic_arm(delays_ms: list[float], arm: str) -> dict[str, object]:
    t_eff = {"none": 4.0, "xy4": 6.0, "cpmg": 5.4, "aegis_selected": 6.6}.get(arm, 4.0)
    records = []
    for delay in delays_ms:
        survival = max(0.0, min(0.999, math.exp(-delay / t_eff)))
        records.append({"delay_ms": delay, "ghz_population": survival, "q_conf": min(0.99, 0.80 + 0.18 * survival)})
    fit = fit_effective_decay(delays_ms, [float(row["ghz_population"]) for row in records])
    return {"arm": arm, "records": records, "fit": fit}


def main() -> None:
    parser = argparse.ArgumentParser(description="Adaptive coherence-sensitive delay-ramp controller.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--delays-ms", default="0,1,2,5")
    parser.add_argument("--output", type=Path, default=Path("adaptive_coherence_controller.json"))
    args = parser.parse_args()
    delays = [float(item.strip()) for item in args.delays_ms.split(",") if item.strip()]
    if args.real:
        ramp = run_delay_ramp(True, args.backend, args.shots, delays, 2026, args.channel)
        survivals = [float(row["ghz_population"]) for row in ramp["records"]]
        arms = [{"arm": "aegis_selected_delay_ramp", "records": ramp["records"], "fit": fit_effective_decay(delays, survivals)}]
    else:
        arms = [synthetic_arm(delays, arm) for arm in ("none", "xy4", "cpmg", "aegis_selected")]
    selected = max(arms, key=lambda arm: float(arm["fit"]["t_eff_ms"]))
    payload = {
        "source": "aegis_adaptive_coherence_controller",
        "real": args.real,
        "backend": args.backend,
        "delays_ms": delays,
        "arms": arms,
        "selected_arm": selected["arm"],
        "selected_t_eff_ms": selected["fit"]["t_eff_ms"],
        "claim_boundary": "Estimates effective workload survival over returned outputs; not intrinsic T1/T2 extension.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
