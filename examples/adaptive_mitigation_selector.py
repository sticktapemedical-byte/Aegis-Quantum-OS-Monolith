from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.ibm_bridge import run_fake_backend_once
from examples.readout_mitigation_comparison import run_readout_mitigation_comparison


def select_policy(raw_quality: float, mitigated_quality: float, mitigation_overhead: float, fallback_epsilon: float = 0.01) -> dict[str, object]:
    uplift = mitigated_quality - raw_quality
    use_mitigation = uplift > (fallback_epsilon + mitigation_overhead)
    return {
        "raw_quality": raw_quality,
        "mitigated_quality": mitigated_quality,
        "mitigation_overhead": mitigation_overhead,
        "uplift": uplift,
        "selected_policy": "readout_mitigation" if use_mitigation else "raw",
        "selection_reason": "uplift_exceeds_cost" if use_mitigation else "uplift_does_not_exceed_cost",
    }


def fake_comparison(shots: int) -> dict[str, object]:
    raw = run_fake_backend_once(shots=shots)
    raw_q = float(raw["ghz_population"])
    mitigated_q = min(0.999, raw_q + 0.012)
    return {
        "source": "fake_readout_mitigation_comparison",
        "raw_ghz_population": raw_q,
        "mitigated_ghz_population": mitigated_q,
        "mitigation_delta": mitigated_q - raw_q,
        "aegis_raw_q_conf": raw["q_conf"],
        "aegis_raw_continuity_gate_passed": raw["continuity_gate_passed"],
        "qom_compact_payload_hex": raw["qom_compact_payload_hex"],
        "merkle_root": raw["merkle_root"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe-then-commit mitigation policy selector.")
    parser.add_argument("--real", action="store_true")
    parser.add_argument("--backend", default="ibm_marrakesh")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--ghz-shots", type=int, default=512)
    parser.add_argument("--calibration-shots", type=int, default=128)
    parser.add_argument("--mitigation-overhead", type=float, default=0.005)
    parser.add_argument("--output", type=Path, default=Path("adaptive_mitigation_selector.json"))
    args = parser.parse_args()
    comparison = (
        run_readout_mitigation_comparison(args.backend, args.ghz_shots, args.calibration_shots, channel=args.channel)
        if args.real else fake_comparison(args.ghz_shots)
    )
    decision = select_policy(
        float(comparison["raw_ghz_population"]),
        float(comparison["mitigated_ghz_population"]),
        args.mitigation_overhead,
    )
    payload = {
        "source": "aegis_adaptive_mitigation_selector",
        "real": args.real,
        "comparison": comparison,
        "decision": decision,
        "claim_boundary": "Selects whether mitigation is worth its overhead for later workloads.",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
