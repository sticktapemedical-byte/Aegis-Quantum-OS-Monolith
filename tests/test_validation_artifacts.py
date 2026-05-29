from __future__ import annotations

import hashlib
import json
from pathlib import Path

from aegis_stats import resource_cost_per_accepted_result, wilson_interval


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_wilson_interval_bounds_known_ghz_run() -> None:
    interval = wilson_interval(3899, 4096)
    assert interval.total == 4096
    assert 0.94 < interval.low < interval.p_hat < interval.high < 0.96


def test_resource_cost_per_accepted_result() -> None:
    assert resource_cost_per_accepted_result(1024, 2) == 512
    assert resource_cost_per_accepted_result(1024, 0) == float("inf")


def test_threshold_freeze_has_required_fields() -> None:
    schema = load_json(ROOT / "schemas" / "threshold_freeze.schema.json")
    payload = load_json(ROOT / "docs" / "validation" / "threshold_freeze.json")
    for field in schema["required"]:
        assert field in payload
    assert payload["q_conf_accept_threshold"] > payload["q_conf_warn_threshold"] > payload["q_conf_fail_threshold"]
    assert "NORMAL" in payload["accepted_governance_states"]


def test_sanitized_manifest_and_artifact_hashes() -> None:
    schema = load_json(ROOT / "schemas" / "job_manifest.schema.json")
    manifest = load_json(ROOT / "docs" / "validation" / "job_manifest.json")
    for field in schema["required"]:
        assert field in manifest
    assert manifest["artifact_count"] == len(manifest["artifacts"])
    assert manifest["artifact_count"] >= 10

    for record in manifest["artifacts"]:
        for field in schema["artifact_required"]:
            assert field in record
        artifact_path = ROOT / record["artifact"]
        assert artifact_path.exists()
        artifact = load_json(artifact_path)
        assert artifact["artifact_sha256"] == record["artifact_sha256"]
        without_hash = dict(artifact)
        artifact_hash = without_hash.pop("artifact_sha256")
        recomputed = hashlib.sha256(json.dumps(without_hash, indent=2, sort_keys=True).encode("utf-8")).hexdigest()
        assert artifact_hash == recomputed


def test_qom_schema_matches_sanitized_artifacts() -> None:
    schema = load_json(ROOT / "schemas" / "qom_record.schema.json")
    for artifact_path in (ROOT / "docs" / "validation" / "raw_counts_sanitized").glob("*.json"):
        payload = load_json(artifact_path)
        for field in schema["required"]:
            assert field in payload
        if payload["qom_compact_payload_hex"]:
            assert payload["qom_compact_payload_bits"] == 176
            assert len(bytes.fromhex(payload["qom_compact_payload_hex"])) == 22
        assert len(payload["merkle_root"]) == 64
