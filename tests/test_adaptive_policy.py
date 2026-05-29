from examples.adaptive_backend_selector import score_backend
from examples.adaptive_mitigation_selector import select_policy


def test_backend_selector_prefers_higher_quality_record():
    low = {"ghz_population": 0.80, "q_conf": 0.82, "round_trip_seconds": 10, "raw_error_rate": 0.20}
    high = {"ghz_population": 0.95, "q_conf": 0.94, "round_trip_seconds": 10, "raw_error_rate": 0.05}
    assert score_backend(high) > score_backend(low)


def test_mitigation_selector_requires_uplift_above_cost():
    assert select_policy(0.90, 0.94, 0.005)["selected_policy"] == "readout_mitigation"
    assert select_policy(0.90, 0.908, 0.005)["selected_policy"] == "raw"
