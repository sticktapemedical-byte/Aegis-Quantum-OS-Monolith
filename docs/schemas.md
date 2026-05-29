# Schemas

The `schemas/` directory contains lightweight schema descriptors for public validation artifacts.

| Schema | Purpose |
| --- | --- |
| `job_manifest.schema.json` | Required fields for `docs/validation/job_manifest.json`. |
| `qom_record.schema.json` | Required `.QOM` and Merkle fields. |
| `threshold_freeze.schema.json` | Required frozen validation thresholds. |
| `probe_record.schema.json` | Required probe output fields. |
| `committed_run.schema.json` | Required committed-run output fields. |
| `coherence_result.schema.json` | Required coherence-controller output fields. |
| `efficiency_result.schema.json` | Required efficiency output fields. |

Validation tests live in:

- `tests/test_schema_validation.py`
- `tests/test_validation_artifacts.py`
- `tests/test_threshold_freeze.py`

The schemas are intentionally lightweight. They are used to prevent missing core fields, not to enforce every possible result shape.

