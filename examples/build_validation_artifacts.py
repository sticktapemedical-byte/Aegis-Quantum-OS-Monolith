from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aegis_stats import wilson_interval


SOURCE_FILES = [
    "ibm_bridge_result.json",
    "ibm_marrakesh_512.json",
    "ibm_marrakesh_4096_ghz.json",
    "ibm_marrakesh_128_delay.json",
    "ibm_kingston_256.json",
    "ibm_fez_256.json",
    "ibm_fast_coherence_marrakesh.json",
    "ibm_long_form_marrakesh.json",
    "ibm_long_form_marrakesh_setpoint.json",
    "ibm_long_form_marrakesh_setpoint_256.json",
    "ibm_long_form_marrakesh_setpoint_1024.json",
    "ibm_readout_mitigation_comparison.json",
    "ibm_vqe_bridge.json",
    "ibm_vqe_bridge_setpoint.json",
    "ibm_depth_stress_comparison.json",
    "ibm_session_batch_loop_fake_smoke.json",
    "accepted_vs_rejected.json",
    "delay_ramp.json",
    "readout_mitigation_repeat.json",
    "adaptive_probe_then_commit.json",
    "adaptive_backend_selector.json",
    "adaptive_layout_selector.json",
    "adaptive_mitigation_selector.json",
    "adaptive_coherence_controller.json",
    "dynamical_decoupling_insertion.json",
    "dynamic_circuit_governance.json",
    "calibration_campaign.json",
    "pulse_level_controls.json",
]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def package_version(name: str) -> str:
    try:
        import importlib.metadata as metadata

        return metadata.version(name)
    except Exception:
        return "not-installed"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sanitize_payload(source_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    final_record = payload.get("records", [{}])[-1] if payload.get("records") else {}
    committed = payload.get("committed_run") or {}
    comparison = payload.get("comparison") or {}
    sanitized: dict[str, Any] = {
        "source_file": source_name,
        "source": payload.get("source"),
        "backend": payload.get("backend") or committed.get("backend") or comparison.get("backend"),
        "job_id": payload.get("job_id") or committed.get("job_id") or comparison.get("job_id"),
        "shots": payload.get("shots") or payload.get("total_shots") or payload.get("ghz_shots") or committed.get("shots") or comparison.get("total_shots") or comparison.get("ghz_shots"),
        "round_trip_seconds": payload.get("round_trip_seconds") or committed.get("round_trip_seconds") or comparison.get("round_trip_seconds"),
        "qom_compact_payload_bits": payload.get("qom_compact_payload_bits") or payload.get("final_qom_compact_payload_bits") or committed.get("qom_compact_payload_bits") or comparison.get("qom_compact_payload_bits") or final_record.get("qom_compact_payload_bits"),
        "qom_compact_payload_hex": payload.get("qom_compact_payload_hex") or payload.get("final_qom_compact_payload_hex") or committed.get("qom_compact_payload_hex") or comparison.get("qom_compact_payload_hex") or final_record.get("qom_compact_payload_hex"),
        "merkle_root": payload.get("merkle_root") or payload.get("final_merkle_root") or committed.get("merkle_root") or comparison.get("merkle_root") or final_record.get("merkle_root"),
    }
    if "ghz_population" in committed and "ghz_population" not in payload:
        payload = dict(payload)
        payload["ghz_population"] = committed["ghz_population"]
        payload["raw_error_rate"] = committed.get("raw_error_rate")
        payload["good_counts_0000_1111"] = committed.get("good_counts_0000_1111")
        payload["total_counts"] = committed.get("total_counts") or committed.get("shots")
    if "counts" in payload:
        sanitized["counts"] = payload["counts"]
    if "raw_counts" in payload:
        sanitized["raw_counts"] = payload["raw_counts"]
    if "ghz_population" in payload:
        good = int(payload.get("good_counts_0000_1111", round(payload["ghz_population"] * payload.get("total_counts", payload.get("shots", 0)))))
        total = int(payload.get("total_counts", payload.get("shots", 0)))
        ci = wilson_interval(good, total)
        sanitized["ghz_population"] = payload["ghz_population"]
        sanitized["raw_error_rate"] = payload.get("raw_error_rate")
        sanitized["ghz_population_wilson_95"] = {"low": ci.low, "high": ci.high}
    if "setpoint_validations_total" in payload:
        ci = wilson_interval(int(payload["setpoint_validations_passed"]), int(payload["setpoint_validations_total"]))
        sanitized["setpoint_validations_passed"] = payload["setpoint_validations_passed"]
        sanitized["setpoint_validations_total"] = payload["setpoint_validations_total"]
        sanitized["setpoint_pass_wilson_95"] = {"low": ci.low, "high": ci.high}
        sanitized["mean_setpoint_abs_error"] = payload.get("mean_setpoint_abs_error")
    if "mitigated_ghz_population" in payload:
        sanitized["raw_ghz_population"] = payload["raw_ghz_population"]
        sanitized["mitigated_ghz_population"] = payload["mitigated_ghz_population"]
        sanitized["mitigation_delta"] = payload["mitigation_delta"]
    if comparison and "mitigated_ghz_population" in comparison:
        sanitized["raw_ghz_population"] = comparison["raw_ghz_population"]
        sanitized["mitigated_ghz_population"] = comparison["mitigated_ghz_population"]
        sanitized["mitigation_delta"] = comparison["mitigation_delta"]
    if "best_energy" in payload:
        sanitized["best_theta"] = payload["best_theta"]
        sanitized["best_energy"] = payload["best_energy"]
    if "records" in payload:
        sanitized["records_summary"] = [
            {
                "batch": record.get("batch"),
                "depth_layers": record.get("depth_layers"),
                "theta": record.get("theta"),
                "ghz_population": record.get("ghz_population"),
                "q_conf": record.get("q_conf"),
                "continuity_gate_passed": record.get("continuity_gate_passed"),
                "governance_states": record.get("governance_states"),
            }
            for record in payload["records"]
        ]
    if "arms" in payload:
        arms = []
        for record in payload["arms"]:
            successes = None
            total = record.get("shots")
            if "survival" in record and total:
                successes = round(float(record["survival"]) * int(total))
            ci = wilson_interval(int(successes), int(total)) if successes is not None and total else None
            selected_by_sequence = bool(payload.get("selected_sequence")) and record.get("sequence") == payload.get("selected_sequence")
            selected_by_arm = bool(payload.get("selected_arm")) and record.get("arm") == payload.get("selected_arm")
            arms.append({
                "arm": record.get("arm"),
                "sequence": record.get("sequence"),
                "status": record.get("status"),
                "survival": record.get("survival"),
                "shots": record.get("shots"),
                "survival_wilson_95": {"low": ci.low, "high": ci.high} if ci else None,
                "selected": selected_by_sequence or selected_by_arm,
                "job_id": record.get("job_id"),
            })
        sanitized["arms_summary"] = arms
        if payload.get("selected_sequence"):
            selected = next((arm for arm in arms if arm.get("selected")), None)
            if selected:
                selected_source = next((record for record in payload["arms"] if record.get("sequence") == selected.get("sequence")), {})
                selected_aegis = selected_source.get("aegis") or {}
                sanitized["job_id"] = sanitized.get("job_id") or selected.get("job_id")
                sanitized["shots"] = sanitized.get("shots") or selected.get("shots")
                sanitized["qom_compact_payload_bits"] = sanitized.get("qom_compact_payload_bits") or selected_aegis.get("qom_compact_payload_bits")
                sanitized["qom_compact_payload_hex"] = sanitized.get("qom_compact_payload_hex") or selected_aegis.get("qom_compact_payload_hex")
                sanitized["merkle_root"] = sanitized.get("merkle_root") or selected_aegis.get("merkle_root")
                sanitized["selected_survival"] = selected.get("survival")
                sanitized["selected_survival_wilson_95"] = selected.get("survival_wilson_95")
    if "acceptance_summary" in payload:
        sanitized["acceptance_summary"] = payload["acceptance_summary"]
        sanitized["success_condition_met"] = payload.get("success_condition_met")
    if "decision" in payload:
        sanitized["decision"] = payload["decision"]
    if "selected_backend" in payload:
        sanitized["selected_backend"] = payload["selected_backend"]
    if "selected_layout" in payload:
        sanitized["selected_layout"] = payload["selected_layout"]
    if "selected_sequence" in payload:
        sanitized["selected_sequence"] = payload["selected_sequence"]
    if "status" in payload:
        sanitized["status"] = payload["status"]
    return sanitized


def main() -> None:
    out_root = ROOT / "docs" / "validation"
    raw_root = out_root / "raw_counts_sanitized"
    raw_root.mkdir(parents=True, exist_ok=True)
    manifest_records = []
    created_utc = datetime.now(timezone.utc).isoformat()
    for name in SOURCE_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        sanitized = sanitize_payload(name, payload)
        sanitized["created_utc"] = created_utc
        sanitized_bytes = json.dumps(sanitized, indent=2, sort_keys=True).encode("utf-8")
        sanitized["artifact_sha256"] = sha256_bytes(sanitized_bytes)
        target = raw_root / name
        target.write_text(json.dumps(sanitized, indent=2, sort_keys=True), encoding="utf-8")
        manifest_records.append(
            {
                "artifact": str(target.relative_to(ROOT)).replace("\\", "/"),
                "source_file": name,
                "backend": sanitized.get("backend"),
                "job_id": sanitized.get("job_id"),
                "shots": sanitized.get("shots"),
                "artifact_sha256": sanitized["artifact_sha256"],
            }
        )
    manifest = {
        "manifest_type": "aegis_sanitized_ibm_validation_manifest",
        "created_utc": created_utc,
        "aegis_commit_hash": git_commit(),
        "python_version": platform.python_version(),
        "qiskit_version": package_version("qiskit"),
        "qiskit_ibm_runtime_version": package_version("qiskit-ibm-runtime"),
        "artifact_count": len(manifest_records),
        "artifacts": manifest_records,
    }
    (out_root / "job_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"written": len(manifest_records), "manifest": "docs/validation/job_manifest.json"}, indent=2))


if __name__ == "__main__":
    main()
