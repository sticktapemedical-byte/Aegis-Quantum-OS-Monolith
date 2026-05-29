import json
from pathlib import Path


def test_required_schema_files_exist_and_parse():
    for name in [
        "probe_record.schema.json",
        "committed_run.schema.json",
        "coherence_result.schema.json",
        "efficiency_result.schema.json",
        "job_manifest.schema.json",
        "qom_record.schema.json",
        "threshold_freeze.schema.json",
    ]:
        data = json.loads((Path("schemas") / name).read_text(encoding="utf-8"))
        assert "required" in data
        assert ("$schema" in data) or ("schema" in data)
