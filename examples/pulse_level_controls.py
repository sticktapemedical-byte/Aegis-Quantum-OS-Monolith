from __future__ import annotations

import argparse
import json
from pathlib import Path


def pulse_policy(omega_drive: float, zne_lambda: float, eta_eff: float, thermal_headroom: float) -> dict[str, object]:
    bounded_omega = max(0.0, min(1.0, omega_drive))
    bounded_zne = max(1.0, min(5.0, zne_lambda))
    bounded_eta = max(0.05, min(1.0, eta_eff))
    safe = thermal_headroom > 0.15 and bounded_omega < 0.92
    return {
        "omega_drive": bounded_omega,
        "zne_lambda": bounded_zne,
        "eta_eff": bounded_eta,
        "thermal_headroom": thermal_headroom,
        "pulse_policy": "ALLOW_TUNED_PULSE_PROFILE" if safe else "DEFER_TO_SAFE_DIGITAL_GATES",
        "zne_enabled": bounded_zne > 1.0,
        "measurement_strength": "attenuated" if bounded_eta < 0.5 else "normal",
        "claim_boundary": "Policy register only; public IBM backends generally do not expose arbitrary pulse-level control.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Pulse-level control policy register harness.")
    parser.add_argument("--omega-drive", type=float, default=0.35)
    parser.add_argument("--zne-lambda", type=float, default=1.0)
    parser.add_argument("--eta-eff", type=float, default=0.85)
    parser.add_argument("--thermal-headroom", type=float, default=0.55)
    parser.add_argument("--output", type=Path, default=Path("pulse_level_controls.json"))
    args = parser.parse_args()
    payload = {"source": "aegis_pulse_level_controls", **pulse_policy(args.omega_drive, args.zne_lambda, args.eta_eff, args.thermal_headroom)}
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
