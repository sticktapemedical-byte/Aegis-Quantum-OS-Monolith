# Policy Catalog

This catalog grounds policy labels in concrete behavior, support level, and Qiskit/Runtime mapping.

| Policy | What it changes | IBM Cloud support | Simulation only? | Requires partner hardware? | Qiskit/runtime mapping |
| --- | --- | --- | --- | --- | --- |
| `RAW_FIXED_BACKEND` | Runs a workload on a fixed backend with no adaptive selection. | Yes | No | No | `SamplerV2(mode=backend)` |
| `AEGIS_BACKEND_SELECTOR` | Probes candidate backends and commits later workload to the highest-scoring backend. | Yes | No | No | `examples/adaptive_backend_selector.py` |
| `AEGIS_PROBE_THEN_COMMIT` | Runs probe jobs, scores them, then sends a later committed workload to selected path. | Yes | No | No | `examples/adaptive_probe_then_commit.py` |
| `AEGIS_LAYOUT_SELECTOR` | Scores candidate qubit-chain layouts using backend target/readout data and commits a selected workload. | Partially | No | No | `backend.target`, preset pass manager |
| `RAW_READOUT` | Uses raw count histograms. | Yes | No | No | standard Sampler counts |
| `BASIC_READOUT_MITIGATION` | Estimates local assignment matrices and applies classical readout correction. | Yes | No | No | calibration circuits + local inversion |
| `AEGIS_MITIGATION_SELECTOR` | Chooses raw vs readout mitigation when uplift exceeds overhead. | Yes | No | No | `examples/adaptive_mitigation_selector.py` |
| `NO_DD` | Runs an idle-window workload without DD-style gates. | Yes | No | No | `delay`, `h`, measurement |
| `XX_ECHO` | Inserts simple X echo gates around an idle delay. | Backend dependent | No | No | ordinary gates/delay compilation |
| `XY4_ECHO` | Inserts X/Y echo-style gates around idle windows. | Backend dependent | No | No | ordinary gates/delay compilation |
| `CPMG_ECHO` | Inserts CPMG-like echo-style gates around idle windows. | Backend dependent | No | No | ordinary gates/delay compilation |
| `AEGIS_COHERENCE_CONTROLLER` | Fits returned survival under delay ramps and selects the best policy arm. | Partially | Synthetic plus real delay-ramp path | No for current harness | `examples/adaptive_coherence_controller.py` |
| `DYNAMIC_CIRCUIT_GOVERNANCE` | Uses mid-circuit measurement/feed-forward when backend supports it. | Backend dependent | No | No | Qiskit `if_test` dynamic circuits |
| `RB_T1_T2_TOMOGRAPHY_CAMPAIGN` | Collects calibration-grade RB, T1/T2/Ramsey, and tomography evidence. | Requires dedicated budget/protocol | Current harness is synthetic by default | No, but requires careful QPU allocation | `examples/calibration_campaign.py` |
| `PULSE_POLICY_REGISTER` | Records pulse-control policy knobs without asserting public pulse access. | Policy only on public IBM | Yes as control policy record | Yes for actual pulse-level control | `examples/pulse_level_controls.py` |
| `DD_REPEAT_CAMPAIGN` | Repeats idle echo/DD-style arms across delay values and reports Wilson intervals. | Backend dependent | No when `--real` is used | No for gate/delay version | `examples/dd_repeat_campaign.py` |
| `QAOA_BRIDGE` | Runs a small MaxCut/QAOA-style workload and governs returned objective quality. | Yes | No when `--real` is used | No | `examples/qaoa_bridge.py` |
| `NEGATIVE_REGRESSION_SUITE` | Preserves blocked, failed, and low-quality runs across backends as regression evidence. | Yes | No when `--real` is used | No | `examples/negative_regression_suite.py` |

Avoid introducing new high-level policy names in public documents unless each one is defined with the same fields above: what changes, IBM Cloud support level, simulation status, partner-hardware requirement, and concrete Qiskit/runtime mapping.
