# AEGIS Adaptive IBM Backend Campaign - 2026-05-29

## Claim Boundary

This campaign measures returned-output governance, adaptive workload selection, mitigation selection, and hardware-feature harness behavior over IBM Quantum Runtime outputs. It does not claim intrinsic device noise suppression, intrinsic T1/T2 improvement, or pulse-level control over public IBM backends.

## Completed Real Backend Runs

| Test | Backend(s) | Real Jobs | Shots | Result |
| --- | --- | ---: | ---: | --- |
| Accepted-vs-rejected quality split | `ibm_marrakesh` | 30 | 7,680 | Success condition met. All mean GHZ `94.88%`; accepted mean `95.25%`; rejected mean `93.05%`; all continuity gates passed. |
| Delay-ramp degradation detection | `ibm_marrakesh` | 4 | 4,096 | Real jobs completed, but monotonic degradation was not observed. GHZ rose from `94.63%` at 0 ms to `97.36%` at 5 ms. |
| Readout mitigation repeat | `ibm_marrakesh` | 10 | 30,720 | Mean raw GHZ `95.77%`; mean mitigated GHZ `97.50%`; mean uplift `+1.73 pp`; raw AEGIS continuity passed. |
| Probe-then-commit selector | `ibm_marrakesh`, `ibm_kingston` | 3 | 1,536 | Selected `ibm_marrakesh`; committed GHZ `95.02%`; continuity passed. |
| Adaptive backend selector | `ibm_marrakesh`, `ibm_kingston` | 3 | 1,536 | Selected `ibm_marrakesh`; committed GHZ `95.70%`; `ibm_kingston` probe continuity failed at `87.11%` GHZ. |
| Adaptive layout selector | `ibm_marrakesh` | 1 | 1,024 | Selected layout `[4, 5, 6, 7]`; committed GHZ `94.24%`; continuity passed. |
| Adaptive mitigation selector | `ibm_marrakesh` | 1 | 3,072 | Selected `readout_mitigation`; raw GHZ `95.12%`; mitigated GHZ `96.68%`; uplift `+1.57 pp`. |
| Adaptive coherence controller | `ibm_marrakesh` | 4 | 2,048 | Real delay-ramp jobs completed; no measurable decay fit observed. The capped sentinel is treated as an invalid/no-decay fit, not a physical lifetime estimate. |
| Dynamical decoupling insertion harness | `ibm_marrakesh` | 4 | 2,048 | Real idle echo/DD-style arms completed. Survival: none `33.59%`, `xx` `67.77%`, `xy4` `70.12%`, `cpmg` `65.82%`; selected `xy4`. |
| Dynamic-circuit governance | `ibm_marrakesh` | 1 | 256 | Real dynamic-circuit job completed. Counts: `00=118`, `11=138`. |

## Non-Queued / Policy Harnesses

| Harness | Result |
| --- | --- |
| Calibration campaign | Recorded `real_calibration_campaign_not_queued_by_default`; RB/T1/T2/tomography requires a dedicated calibrated shot budget. |
| Pulse-level controls | Emitted policy register: `ALLOW_TUNED_PULSE_PROFILE`; public IBM backends generally do not expose arbitrary pulse-level control. |

## Operational Notes

- IBM Runtime Sessions are not available on the current open plan. The session-batch code fell back to normal job mode and recorded the fallback reason.
- `ibm_fez` had a high queue and one probe job was cancelled by IBM. The adaptive scripts were hardened to record failed probes and continue with successful backends.
- The delay-ramp and coherence-controller runs did not expose monotonic decay under the tested compiled delay path. These should be presented as negative/inconclusive for degradation detection, not as coherence improvement.
- The strongest positive results from this campaign are the accepted-vs-rejected split, readout mitigation repeat uplift, backend selection favoring `ibm_marrakesh`, dynamic-circuit execution, and DD-style idle echo arm comparison.
- The DD-style result is a single workload/run comparison. It supports that the harness can compare control-policy candidates, not that AEGIS improves intrinsic coherence.
- The ablation workflow now separates raw target quality from governed software score so raw-only and full-AEGIS modes are not compared through one overloaded metric.
- The follow-up DD repeat, QAOA bridge, and negative-regression wrappers were added after this campaign. Real IBM execution is currently recorded as blocked by IBM Cloud/QPU availability in `AEGIS_IBM_Maintenance_Blocked_Campaign_2026-05-29.md`.

## Most Defensible Public Claim

AEGIS demonstrated real IBM Cloud QPU returned-output governance with accepted-output quality separation, repeated readout-mitigation tracking, adaptive backend selection, compact `.QOM` metadata, and Merkle lineage over a sanitized validation vault.

## Sanitized Artifact Rollup

After regenerating sanitized artifacts, the validation vault contains:

- Sanitized artifacts represented: `32`
- Total tracked shots in sanitized summaries: `71,424`
- Accepted artifacts: `25`
- Shots per accepted artifact: `2,856.96`
- Holdout artifacts: `10`
- Train artifacts: `18`

See:

- `docs/validation/job_manifest.json`
- `docs/validation/efficiency_summary.json`
- `docs/validation/blind_holdout.json`
- `docs/validation/ablation_workflow.json`
- `docs/validation/reports/validation_summary.md`
