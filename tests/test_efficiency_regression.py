from aegis_efficiency import summarize_efficiency


def test_efficiency_does_not_accept_all_bad_records():
    records = [
        {"shots": 50, "ghz_population": 0.1, "q_conf": 0.2, "continuity_gate_passed": False},
        {"shots": 50, "ghz_population": 0.2, "q_conf": 0.3, "continuity_gate_passed": False},
    ]
    summary = summarize_efficiency(records)
    assert summary.accepted_results == 0
    assert summary.rerun_rate == 1.0
