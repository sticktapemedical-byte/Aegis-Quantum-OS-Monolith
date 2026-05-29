# Implementation Status

This table separates implemented code, simulated harnesses, real IBM Cloud requirements, partner-level hardware requirements, and claims that are not currently earned.

| Component | Status | Evidence |
| --- | --- | --- |
| IBM count ingestion | Implemented / prior validation | `examples/ibm_bridge.py`, `docs/validation/raw_counts_sanitized/*.json` |
| `.QOM` lineage | Implemented | `aegis_kernel.py`, `tests/test_kernel.py`, sample payloads in sanitized artifacts |
| Merkle lineage | Implemented | `aegis_kernel.py`, validation artifacts with `merkle_root` |
| Schema folder | Implemented | `schemas/`, `tests/test_schema_validation.py` |
| Schema validation tests | Implemented | `tests/test_schema_validation.py` |
| Threshold freeze | Implemented | `docs/validation/threshold_freeze.json`, `tests/test_threshold_freeze.py` |
| Sanitized artifact writer | Implemented | `examples/build_validation_artifacts.py`, `docs/validation/job_manifest.json` |
| Confidence intervals | Implemented | `aegis_stats.py`, validation tests |
| Baseline comparator | Implemented | `examples/baseline_comparator.py`, `docs/validation/baseline_comparison.json` |
| Accepted/rejected split | Implemented / real IBM run completed | `examples/accepted_vs_rejected.py`, `docs/validation/raw_counts_sanitized/accepted_vs_rejected.json` |
| Backend selector | Implemented / real IBM run completed | `examples/adaptive_backend_selector.py`, campaign report |
| Probe-then-commit controller | Implemented / real IBM run completed | `examples/adaptive_probe_then_commit.py`, campaign report |
| Layout selector | Implemented as candidate layout scoring / real commit completed | `examples/adaptive_layout_selector.py`, campaign report |
| Adaptive mitigation selector | Implemented / real IBM run completed | `examples/adaptive_mitigation_selector.py`, campaign report |
| Adaptive DD/coherence controller | Implemented as delay-ramp and DD-style harness | `examples/adaptive_coherence_controller.py`, `examples/dynamical_decoupling_insertion.py` |
| Dynamic-circuit governance | Implemented where IBM backend supports dynamic circuits | `examples/dynamic_circuit_governance.py`, real `ibm_marrakesh` result |
| RB/T1/T2/tomography campaign | Harness implemented; real campaign not queued by default | `examples/calibration_campaign.py` |
| Pulse-level controls | Policy register implemented; public IBM pulse access not claimed | `examples/pulse_level_controls.py` |
| Efficiency metrics | Implemented | `aegis_efficiency.py`, `examples/efficiency_report.py` |
| Blind holdout workflow | Implemented | `examples/blind_holdout.py`, `docs/validation/blind_holdout.json` |
| Ablation workflow | Implemented | `examples/ablation_workflow.py`, `docs/validation/ablation_workflow.json` |
| Plot/report generation | Implemented as CSV/Markdown/SVG/PDF | `examples/generate_validation_report.py`, `examples/generate_master_validation_pdf.py` |
| Publication checklist | Implemented | `docs/publication_checklist.md` |
| Target claim stage | Not earned as a broad claim | Requires controlled baseline comparisons, larger repeats, backend calibration snapshots, and successful holdout/ablation evidence |
| Partner-level hardware integration | Not currently supported | Would require hardware telemetry or vendor/partner access beyond public IBM Runtime |

