# AEGIS Adaptive IBM Validation Plan

This document maps the QPU upgrade plan to the current repository state. The claim boundary remains narrow: AEGIS currently governs returned IBM Quantum outputs and can select later workloads; it does not modify a running QPU job in real time.

## Implemented

| Plan item | Repo status |
| --- | --- |
| Claim boundary language | README, validation report, and roadmap state that AEGIS is a classical post-processing and workload-governance layer. |
| Confidence intervals | `aegis_stats.py` provides Wilson intervals; validation artifacts and tests use them. |
| Sanitized artifact vault | `docs/validation/raw_counts_sanitized/` and `docs/validation/job_manifest.json` store public-safe count histograms, job IDs, derived metrics, hashes, and version metadata. |
| Exact circuit specs | `circuits/` contains GHZ, phase-sweep, VQE-style toy-H2, and depth-stress specifications. |
| Baseline comparison | `examples/baseline_comparator.py` builds raw-vs-governed-vs-mitigated summaries. |
| Threshold freeze | `docs/validation/threshold_freeze.json` freezes public thresholds before follow-up interpretation. |
| CI and tests | `.github/workflows/test.yml` runs the Python test suite; `tests/` checks kernel safety invariants and validation artifacts. |
| Backend discovery | `examples/ibm_backend_discovery.py` lists accessible operational backends without submitting jobs. |
| Session-style batch loop | `examples/session_batch_loop.py` processes returned batches immediately and falls back to normal jobs if IBM Runtime Sessions are unavailable. |
| Probe-then-commit controller | `examples/adaptive_probe_then_commit.py` probes candidate backends and sends a later committed workload to the selected backend. |
| Accepted-vs-rejected quality split | `examples/accepted_vs_rejected.py` compares accepted, rejected, and all returned batches. |
| Delay-ramp degradation detection | `examples/delay_ramp.py` runs GHZ workloads with configurable idle delays. |
| Readout mitigation repeat study | `examples/readout_mitigation_repeat.py` repeats raw-vs-basic-readout-mitigation comparisons. |
| Adaptive backend selector | `examples/adaptive_backend_selector.py` probes candidate backends and commits to the highest AEGIS score. |
| Adaptive layout selector | `examples/adaptive_layout_selector.py` ranks candidate qubit chains and can commit a selected workload. |
| Adaptive mitigation selector | `examples/adaptive_mitigation_selector.py` compares raw vs readout-mitigated quality and selects a later policy. |
| Adaptive coherence controller | `examples/adaptive_coherence_controller.py` fits effective delay-ramp survival and selects the best policy arm in synthetic mode or real delay-ramp mode. |
| Dynamical decoupling insertion harness | `examples/dynamical_decoupling_insertion.py` builds idle-window echo/DD-style arms and runs synthetic by default or real if backend/API support allows. |
| Dynamic-circuit governance harness | `examples/dynamic_circuit_governance.py` builds a small mid-circuit measurement/feed-forward template and reports unsupported cleanly when unavailable. |
| RB/T1/T2/tomography campaign harness | `examples/calibration_campaign.py` produces synthetic calibration proxies and reserves `--real` for a dedicated calibrated hardware campaign. |
| Pulse-level control policy registers | `examples/pulse_level_controls.py` records Omega-drive, ZNE lambda, eta-eff, and thermal-headroom policy decisions without claiming public-backend pulse access. |
| Resource efficiency summary | `examples/efficiency_report.py` summarizes shots per accepted artifact from the sanitized vault. |
| Efficiency utilities | `aegis_efficiency.py` computes accepted results, rerun rate, and shots/jobs per accepted result. |
| Blind holdout workflow | `examples/blind_holdout.py` creates deterministic train/holdout splits over sanitized artifacts. |
| Ablation workflow | `examples/ablation_workflow.py` compares raw-only, no-anchor, no-lineage, and full-AEGIS modes over artifacts. |
| Plot/report generation | `examples/generate_validation_report.py` emits CSV, Markdown, and SVG summary artifacts. |
| Publication checklist | `docs/publication_checklist.md` documents claim-safe publication requirements. |

## Ready-To-Run Real Backend Commands

These commands spend IBM Quantum runtime. Keep shot counts low unless deliberately running a statistical study.

```powershell
python examples/accepted_vs_rejected.py --real --backend ibm_marrakesh --batches 30 --shots 256 --accept-threshold 0.94 --output accepted_vs_rejected.json
python examples/delay_ramp.py --real --backend ibm_marrakesh --shots 1024 --delays-ms 0,1,2,5 --output delay_ramp.json
python examples/readout_mitigation_repeat.py --real --backend ibm_marrakesh --repeats 10 --ghz-shots 1024 --calibration-shots 256 --output readout_mitigation_repeat.json
python examples/adaptive_probe_then_commit.py --real --backends ibm_marrakesh,ibm_kingston,ibm_fez --probe-shots 256 --commit-shots 1024 --output adaptive_probe_then_commit.json
python examples/adaptive_backend_selector.py --real --backends ibm_marrakesh,ibm_kingston,ibm_fez --probe-shots 256 --commit-shots 1024 --output adaptive_backend_selector.json
python examples/adaptive_layout_selector.py --real --backend ibm_marrakesh --probe-shots 256 --commit-shots 1024 --output adaptive_layout_selector.json
python examples/adaptive_mitigation_selector.py --real --backend ibm_marrakesh --ghz-shots 1024 --calibration-shots 256 --output adaptive_mitigation_selector.json
python examples/adaptive_coherence_controller.py --real --backend ibm_marrakesh --shots 512 --delays-ms 0,1,2,5 --output adaptive_coherence_controller.json
python examples/dynamical_decoupling_insertion.py --real --backend ibm_marrakesh --shots 512 --delay-us 50 --output dynamical_decoupling_insertion.json
python examples/dynamic_circuit_governance.py --real --backend ibm_marrakesh --shots 256 --output dynamic_circuit_governance.json
python examples/efficiency_report.py --output docs/validation/efficiency_summary.json
python examples/blind_holdout.py --output docs/validation/blind_holdout.json
python examples/ablation_workflow.py --output docs/validation/ablation_workflow.json
python examples/generate_validation_report.py --outdir docs/validation/reports
```

## Still Future Work

| Plan item | Status |
| --- | --- |
| Dynamical decoupling controller | Idle-window echo/DD-style insertion harness is implemented; pulse-calibrated DD scheduler insertion remains backend/API dependent. |
| Dynamic-circuit feedback | Mid-circuit template harness is implemented; real execution depends on backend/API support. |
| RB/T1/T2/tomography campaign | Synthetic campaign harness is implemented; real calibrated campaign requires explicit shot budget and a dedicated protocol. |
| Publication PNG plots | SVG/CSV/Markdown report generation is implemented; PNG generation is deferred to avoid extra plotting dependencies. |

## Operating Rule

When presenting results, describe them as returned-output governance, quality gating, and adaptive workload selection. Use stronger language only after AEGIS changes a future submitted workload and beats fixed baselines under the same backend and calibration window.
