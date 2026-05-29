from examples.calibration_campaign import synthetic_rb, synthetic_t1_t2, synthetic_tomography
from examples.dynamical_decoupling_insertion import synthetic_dd_arm
from examples.pulse_level_controls import pulse_policy


def test_synthetic_dd_selectors_have_survival_values():
    none = synthetic_dd_arm("none", 50.0)
    xy4 = synthetic_dd_arm("xy4", 50.0)
    assert 0 <= none["survival"] <= 1
    assert xy4["survival"] > none["survival"]


def test_calibration_campaign_proxies_are_bounded():
    rb = synthetic_rb(1, [1, 2, 4], 128)
    t = synthetic_t1_t2(1, [0, 10], 128)
    tomo = synthetic_tomography(1, 128)
    assert rb["epc_estimate"] > 0
    assert t["t1_us"] > 0 and t["t2_us"] > 0
    assert 0 <= tomo["fidelity_proxy"] <= 1


def test_pulse_policy_defers_when_unsafe():
    safe = pulse_policy(0.2, 2.0, 0.8, 0.6)
    unsafe = pulse_policy(0.99, 2.0, 0.8, 0.6)
    assert safe["pulse_policy"] == "ALLOW_TUNED_PULSE_PROFILE"
    assert unsafe["pulse_policy"] == "DEFER_TO_SAFE_DIGITAL_GATES"
