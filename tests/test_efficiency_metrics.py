from aegis_efficiency import is_accepted, summarize_efficiency


def test_efficiency_summary_counts_reruns_and_cost():
    records = [
        {"shots": 100, "ghz_population": 0.95, "q_conf": 0.94, "continuity_gate_passed": True, "qom_compact_payload_hex": "aa", "merkle_root": "bb"},
        {"shots": 100, "ghz_population": 0.70, "q_conf": 0.80, "continuity_gate_passed": False, "qom_compact_payload_hex": "aa", "merkle_root": "bb"},
    ]
    summary = summarize_efficiency(records)
    assert summary.accepted_results == 1
    assert summary.rerun_count == 1
    assert summary.rerun_rate == 0.5
    assert summary.shots_per_accepted_result == 200


def test_acceptance_requires_lineage_for_generic_records():
    assert is_accepted({"qom_compact_payload_hex": "aa", "merkle_root": "bb"}) is True
    assert is_accepted({"qom_compact_payload_hex": "", "merkle_root": "bb"}) is False
