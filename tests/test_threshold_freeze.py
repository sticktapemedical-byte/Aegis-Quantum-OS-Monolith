import json
from pathlib import Path


def test_threshold_freeze_has_nonempty_policy_fields():
    data = json.loads(Path("docs/validation/threshold_freeze.json").read_text(encoding="utf-8"))
    assert data["q_conf_accept_threshold"] >= data["q_conf_warn_threshold"]
    assert "selector_weights" in data
    assert "resource_cost_weights" in data
