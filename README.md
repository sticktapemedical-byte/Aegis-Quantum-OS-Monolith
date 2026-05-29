# AEGIS Site Reliability Control-Plane Simulation Framework

> **Scope in one sentence:** AEGIS is a site reliability control-plane simulation framework for probabilistic telemetry and quantum-inspired hardware-interface research. It performs classical post-processing, governance, serialization, and lineage over observed data. It is not a physical quantum operating system, not a hardware product, and not a claim that software changes device-level quantum noise.

## What This Is / What This Is Not

| This repository is | This repository is not |
|---|---|
| A Python simulation framework for reliability governance around probabilistic telemetry. | A physical quantum operating system or deployed hardware controller. |
| A reference implementation of reliability control-plane ideas: observability, gating, fail-closed states, lineage, and reviewer metrics. | A claim that software removes, suppresses, or physically alters quantum noise. |
| A reproducible benchmark harness with tests, Monte Carlo runs, Qiskit bridge examples, and JSON artifacts. | A validated production deployment on real quantum hardware. |
| A noncommercial research/portfolio codebase with commercial licensing reserved separately. | A permission grant for commercial platform integration. |

For technical review, read the claims as **simulation claims unless a section explicitly says otherwise**. See `VALIDATION.md`, `ASSUMPTIONS.md`, `ROADMAP.md`, and `docs/runtime_boundaries.md` for grounding boundaries.

## Executive Summary

AEGIS explores a site reliability engineering approach for operating high-entropy probabilistic systems with classical reliability controls. The project uses “Q-SRE” as shorthand for that research direction, but the implemented artifact is a simulation framework.

AEGIS is the reference implementation: a control plane and simulation framework for mediating probabilistic hardware interfaces. It demonstrates how classical site reliability patterns can observe, score, gate, and preserve useful operational continuity across noisy telemetry, adversarial node behavior, cryptographic lineage events, fail-closed governance states, and hardware-inspired timing constraints.

Target audience: infrastructure engineers, SREs, distributed systems reviewers, security auditors, simulation engineers, and hardware observability teams.

Scope note: this is a software simulation and control-plane framework. It does not claim to physically modify quantum hardware, erase physical noise, or bypass known limits of quantum mechanics. Its core claim is classical software-mediated unsafe-output prevention, observability, containment, serialization, and reproducible artifact generation around probabilistic telemetry.

## Terminology

**Q-SRE** is a term coined for this project. It means applying classical Site Reliability Engineering patterns, such as observability, governance, fault isolation, continuity tracking, fail-closed behavior, and lineage, to noisy probabilistic systems. Those systems may include simulator outputs, real quantum processor count histograms, or other high-entropy telemetry streams.

**`.QOM`** means **Quality Orchestration Metadata** in this repository. A `.QOM` frame is a compact 176-bit binary metadata structure carrying phase, confidence/coherence, lifecycle, trust, risk/backaction proxy, governance, and policy-context metadata. It is not a network TLD and not a claim of quantum transport.

For technical sections, the project can also be read as a **Probabilistic SRE Control Plane** or **Aegis Continuity Kernel**.

## Current Execution Model And Limitations

AEGIS currently functions as a **classical post-processing governance layer**.

1. IBM Quantum Runtime executes a circuit on hardware.
2. Raw count histograms are returned after job completion.
3. AEGIS ingests those results, performs continuity tracking, wrapped-delta phase unwrapping, trust evaluation, governance decisions, `.QOM` serialization, and Merkle logging.

This is not real-time control during quantum execution. AEGIS does not influence a quantum circuit while it is running on the QPU.

Near-term roadmap:

- Use Qiskit Runtime Sessions to keep quantum/classical resources warm across multiple short jobs.
- Process each returned batch immediately through AEGIS instead of waiting for one monolithic experiment.
- Use AEGIS governance outputs to select the next submitted circuit batch in a hybrid classical-quantum loop.
- Explore IBM dynamic circuits for hardware-supported mid-circuit measurement/feed-forward where applicable, with AEGIS still governing the returned data stream.

## Architecture Diagram and Sample Output

![AEGIS Site Reliability Control Plane Architecture](docs/architecture.svg)

Example reviewer-mode output fields are included at `docs/sample_reviewer_output.json`. Generate fresh local output with:

`python aegis_os.py --reviewer-mode --output aegis_os_report.json`

## License And Commercial Use

This repository is published for noncommercial research, evaluation, education, benchmarking, and technical review under the terms in `LICENSE`.

Commercial use is not included in the public license. Production deployment, proprietary product integration, hosted service use, paid consulting delivery, internal enterprise platform integration, commercial redistribution, or use of the project identity in a commercial offer requires a separate written commercial license.

See `COMMERCIAL_LICENSE.md` for the commercial-use notice.

## Support the Engineering Runway

If you want to back the development of this open-source control plane simulation, quantum error mitigation tuning metrics, or low-level FPGA register targets, consider supporting the research runway:

- **Support via Buy Me a Coffee:** [Support Aegis Reliability Lab on Buy Me a Coffee](https://buymeacoffee.com/aegisqsrelab)

## Core Technical Metrics

Current public simulation metrics from the repository's synthetic benchmark suite:

- Unsafe-Output Prevention Efficiency, `UOP_eff`: `99.63%`
- Unnecessary Shutdown Rate, `USR`: `0.00%`
- Telemetry compression model ratio: `14.2x`
- Compact `.QOM` metadata frame: `176 bits`
- Public v1 UOP target: `99.49%`
- Systemic stretch UOP target: `99.90%`
- Theoretical cascade boundary target: `99.925%`

Observed synthetic cascade variance reductions:

- Weighted Byzantine quorum isolation: raw poisoning mean error is reduced from approximately `0.3940` to `0.0188`.
- Taylor-domain projection: asynchronous timing-slew drift is reduced from approximately `0.0633` to `0.0055`.
- Wrapped-delta phase unwrapping: wrapped phase-cut acceleration variance is reduced from approximately `0.2354` to `8.09e-08` in synthetic trials.

## Real Hardware Results: IBM Quantum Runtime

On May 28, 2026, the optional IBM bridge executed a short validation set on real IBM Quantum hardware. The full ledger is stored at [`docs/validation/AEGIS_Master_IBM_Quantum_Validation_Report.md`](docs/validation/AEGIS_Master_IBM_Quantum_Validation_Report.md).

This is a real ingestion and governance test against noisy hardware output. AEGIS does classical post-processing of IBM count histograms after execution. It is not presented as a broad benchmark of IBM hardware, not a calibration claim, and not evidence that the software changes physical device noise.

Master ledger highlights:

- Backends used: `ibm_marrakesh`, `ibm_kingston`, `ibm_fez`
- Real backend jobs represented: `15`
- Total real hardware shots represented: `25,984` across validation jobs
- Initial 4-qubit GHZ run on `ibm_marrakesh`: `94.24%` GHZ population (`965/1024` shots)
- Same-backend repeatability run on `ibm_marrakesh`: `96.09%` GHZ population (`492/512` shots)
- High-shot GHZ stability run on `ibm_marrakesh`: `95.19%` GHZ population (`3899/4096` shots), continuity passed, `NORMAL`
- Cross-device GHZ runs: `ibm_kingston` at `92.58%`, `ibm_fez` at `83.59%`
- Fast single-qubit coherence/readout pass: `q_conf=0.96972`, continuity passed, `NORMAL`
- Corrected commanded setpoint sweeps: `15/15` setpoint validations passed across 128-shot, 256-shot, and 1024-shot sweeps
- High-shot commanded setpoint sweep on `ibm_marrakesh`: `5/5` setpoints passed, mean absolute setpoint error `0.0043`, `5120` total shots
- Basic readout mitigation comparison: raw GHZ population `95.41%`, locally mitigated GHZ population `96.86%`, delta `+1.45 percentage points`
- Small VQE-style variational scan: best toy-H2 energy `-1.0150` at `theta=0.2`; corrected setpoint version passed `3/3` continuity gates
- Cross-depth GHZ stress: depth-stressed circuits drove target-state population down to `0.78%` to `7.62%`, demonstrating high-error ingestion and fail-safe non-pass decisions
- Compact `.QOM` frames generated at `176 bits` with Merkle lineage roots

Result: the AEGIS control-plane bridge successfully ingested real noisy IBM Quantum counts, converted them into the repository's telemetry schema, evaluated continuity and commanded-setpoint gates, and generated compact `.QOM` metadata frames with Merkle lineage.

Statistical rigor note: these are early, short-shot validation runs intended to prove end-to-end integration. They are not sufficient for device-level statistical claims. Stronger future studies should use more repetitions per condition, higher shot counts, confidence intervals, and controlled backend calibration snapshots.

## 10-Step Canonical Runtime Loop

1. `INGEST_TELEMETRY`
2. `RECOMPUTE_KAPPA_VECTOR`
3. `TAYLOR_KINETIC_PROJECTION`
4. `RIEMANN_MANIFOLD_UNWRAP`
5. `ESTIMATE_PROXY_STATE`
6. `VERIFY_WEIGHTED_BFT_QUORUM`
7. `CROSS_CHECK_ROLLING_ANCHOR`
8. `STATE_GOVERNOR_BITMASK`
9. `EMIT_QOM_SNAPSHOT`
10. `WRITE_MERKLE_LEDGER`

## Architecture Overview

### Network Mesh Layer

Models decentralized data transport, live stress injection, `.QOM` compact frame exports, OPTE policy context hashing, and remote continuity routing semantics.

### Regional Hub Nodes

Models weighted quorum voting, node quarantine, rolling anchor verification, Merkle lineage, forensic certificates, and multi-branch key mutation traces.

### Acceleration Tier

Models math offload for Taylor-domain kinetic phase normalization, wrapped-delta phase unwrapping, weighted vector fusion, Monte Carlo cascade efficiency estimation, and reviewer-mode telemetry metrics.

### Register Abstraction

Models low-level hardware-style diagnostics:

- `G(t)` boundary gating
- hardware register handoff slack
- O-quantization timing windows
- relativistic timestamp compensation
- ZNE tuning
- RTOS queue depth and lockhold latency
- cryogenic thermal scheduling and joule-density cost

## Runtime Failure Boundary Rules

The detailed failure-boundary notes were moved to `docs/runtime_boundaries.md` to keep the README focused. In short, the simulator models low-order fallback, phase-branch recovery, staged cryptographic sealing, fail-closed governance, and forensic branch tombstones.

## Quick Start

Prerequisites:

- Python 3.10 or newer recommended
- Core simulator and monitor: no external Python dependencies
- Test runner: `pytest` recommended
- Qiskit bridge example: optional `qiskit` and `qiskit-aer`

Run the terminal simulation:

`python aegis_os.py`

Run reviewer-mode terminal output:

`python aegis_os.py --reviewer-mode`

Run tests and reviewer-mode output in one command:

`python -m pytest tests && python aegis_os.py --reviewer-mode`

Equivalent reviewer-mode toggle:

`python aegis_os.py --mode reviewer`

Environment-variable reviewer toggle:

`$env:AEGIS_REVIEWER_MODE="1"; python aegis_os.py`

Run the live monitor:

`python aegis_monitor.py --host 127.0.0.1 --port 8765`

Open:

`http://127.0.0.1:8765`

The monitor includes a Qiskit simulator ingestion panel with live QST-style overlap fidelity, `T1`/`T2` relaxation/dephasing readouts, Qiskit noise-scale controls, a QEM calibration toggle, and a `STATE_LEAKAGE_RECON` stress mode that reports leaked channel indices and Solve-for-X reconstruction score. The panel also exposes `Run Qiskit Pass`, `Stop Qiskit Only`, `Save Qiskit JSON`, `Export Qiskit JSON`, and `Import Qiskit JSON` controls so reviewers can generate a bridge artifact, cancel only the Qiskit bridge loop without stopping the live monitor, persist it on the local server, download it, or reload a prior bridge run.

Run automated regression tests:

`python -m pip install -r requirements-dev.txt`

`python -m pytest tests/`

Run the optional Qiskit Aer bridge:

`python examples/qiskit_bridge.py`

If Qiskit is not installed, install the optional integration packages in a separate environment:

`python -m pip install -r requirements-qiskit.txt`

## Repository File Map

- `docs/architecture.svg`: simplified architecture diagram for reviewers.
- `docs/ibm_quantum_setup.md`: optional IBM Quantum bridge setup and operational cautions.
- `docs/runtime_boundaries.md`: detailed simulated failure-boundary rules.
- `docs/sample_reviewer_output.json`: compact example of reviewer-mode output fields.
- `docs/validation/job_manifest.json`: sanitized validation manifest with artifact hashes, versions, backends, job IDs, and shot counts.
- `docs/validation/baseline_comparison.json`: raw-vs-governed-vs-mitigated comparison generated from sanitized artifacts.
- `docs/validation/raw_counts_sanitized/`: sanitized IBM result artifacts. These include count histograms and derived metrics, but exclude tokens, account identifiers, and local paths.
- `docs/validation/threshold_freeze.json`: frozen public validation thresholds used to avoid post-hoc tuning accusations.
- `docs/validation/efficiency_summary.json`: resource-efficiency rollup over sanitized validation artifacts.
- `docs/validation/blind_holdout.json`: deterministic train/holdout split over sanitized artifacts.
- `docs/validation/ablation_workflow.json`: ablation comparison over raw-only, no-anchor, no-lineage, and full-AEGIS modes.
- `docs/validation/reports/`: generated CSV, Markdown, and SVG validation report artifacts.
- `docs/adaptive_validation_plan.md`: current implementation checklist and ready-to-run IBM backend validation commands.
- `docs/publication_checklist.md`: claim-safe checklist for public reports and submissions.
- `schemas/`: lightweight schema descriptors for validation artifacts, `.QOM` records, and threshold-freeze files.
- `circuits/`: exact circuit specifications for GHZ, phase setpoint, VQE-style toy H2, and depth-stress workloads.
- `.github/FUNDING.yml`: external support link configuration.
- `examples/qiskit_bridge.py`: optional Qiskit Aer bridge that maps noisy GHZ circuit counts into AEGIS telemetry inputs.
- `examples/ibm_bridge.py`: optional IBM Quantum Runtime bridge with fake-backend smoke testing and explicit real-hardware mode.
- `examples/build_validation_artifacts.py`: builds sanitized validation artifacts from local IBM result files.
- `examples/baseline_comparator.py`: summarizes raw GHZ, AEGIS-governed GHZ, readout mitigation uplift, and setpoint pass-rate metrics.
- `examples/ibm_backend_discovery.py`: lists accessible IBM Quantum backends without submitting jobs.
- `examples/accepted_vs_rejected.py`: compares accepted, rejected, and all returned batch quality.
- `examples/delay_ramp.py`: runs a configurable idle-delay GHZ ramp to observe degradation detection.
- `examples/readout_mitigation_repeat.py`: repeats raw-vs-basic-readout-mitigation comparisons.
- `examples/adaptive_probe_then_commit.py`: probes candidates and sends a later committed workload to the selected path.
- `examples/adaptive_backend_selector.py`: probes candidate IBM backends and commits to the highest AEGIS score.
- `examples/adaptive_layout_selector.py`: ranks candidate qubit-chain layouts and can commit a selected workload.
- `examples/adaptive_mitigation_selector.py`: selects raw vs readout-mitigated policy based on uplift and overhead.
- `examples/adaptive_coherence_controller.py`: fits effective delay-ramp survival and selects a coherence-sensitive policy arm.
- `examples/dynamical_decoupling_insertion.py`: builds idle-window echo/DD-style candidate circuits where backend support allows.
- `examples/dynamic_circuit_governance.py`: probes a small mid-circuit measurement/feed-forward workflow.
- `examples/calibration_campaign.py`: RB/T1/T2/tomography campaign harness with synthetic defaults.
- `examples/pulse_level_controls.py`: pulse-policy register harness for Omega-drive, ZNE lambda, measurement efficiency, and thermal headroom.
- `examples/blind_holdout.py`: creates deterministic blind train/holdout artifact splits.
- `examples/ablation_workflow.py`: compares partial AEGIS modes over validation artifacts.
- `examples/generate_validation_report.py`: generates CSV, Markdown, and SVG report assets.
- `examples/efficiency_report.py`: produces resource-efficiency summaries from the sanitized validation vault.
- `tests/test_kernel.py`: pytest-compatible regression suite for crypto sealing, holdover aborts, and wrapped-delta phase continuity.
- `tests/test_validation_artifacts.py`: validates Wilson confidence intervals, threshold-freeze fields, sanitized manifest hashes, and `.QOM` artifact structure.
- `requirements-dev.txt`: local test-runner dependency file.
- `requirements-qiskit.txt`: optional Qiskit bridge dependency file.
- `aegis_kernel.py`: core control-plane logic, mathematical registers, governance states, Monte Carlo metrics, `.QOM` frames, Merkle lineage, and multiplicative trust matrices.
- `aegis_os.py`: terminal runner managing deterministic execution, report output, and reviewer-mode telemetry switches.
- `aegis_monitor.py`: loopback HTTP server orchestrating the live diagnostic dashboard, stressor controls, exports, and health endpoints.
- `README.md`: technical specification handbook and deployment guide.
- `ROADMAP.md`: implemented vs. simulated vs. future hardware target vs. speculative research boundaries.
- `VALIDATION.md`: measured simulation claims and non-measured boundaries.
- `ASSUMPTIONS.md`: explicit simulation assumptions.
- `LICENSE`: PolyForm Noncommercial License 1.0.0.
- `COMMERCIAL_LICENSE.md`: commercial-use notice and contact path.

## Automated Testing

The `tests/` suite verifies hard safety invariants:

- Crypto invalidation: an induced key/signature slip sets `CRYPTO_SEAL`, drops the continuity gate, and closes the hardware register gate.
- Holdover breach: an elapsed tracking window beyond the safe phase-error ceiling triggers `CIRCUIT_ABORT` and marks `HOLDOVER_BREACH`.
- Phase unwrap continuity: aggressive `[-pi, +pi)` branch-cut crossings remain continuous after wrapped-delta unwrapping, with acceleration variance below `8.09e-08`.

The tests use plain Python assertions and are compatible with pytest:

`python -m pytest tests/`

## Validation and Grounding

This project is a simulation framework for reliability-governance behavior around probabilistic telemetry, not a claim of measured physical quantum hardware performance. See `VALIDATION.md` and `ASSUMPTIONS.md` for the current boundary between measured simulation results, theoretical projections, and non-modeled hardware behavior.

Grounded checks include:

- weighted Byzantine filtering against synthetic poisoned-node trials
- wrapped-delta phase unwrapping across `[-pi, pi)` branch cuts
- unsafe-output prevention across deterministic stress scenarios
- Merkle/HMAC ledger integrity checks
- `.QOM` compact payload bit-width validation

## `.QOM` Compact Payload Layout

The compact `.QOM` payload is generated as a real 22-byte big-endian binary struct in `aegis_kernel.py`, not as a JSON placeholder. The implementation is `AegisContinuityKernel.emit_compact_qom_payload(...)`:

`struct.pack(">IHHHHHQ", phase_u32, coherence_u16, lifecycle_u16, trust_u16, backaction_u16, governance_u16, opte_u64)`

That layout is:

| Field | Type | Bits |
|---|---:|---:|
| phase estimate | unsigned int | 32 |
| coherence / confidence | unsigned short | 16 |
| lifecycle epoch | unsigned short | 16 |
| trust index | unsigned short | 16 |
| backaction/risk proxy | unsigned short | 16 |
| governance bitmask | unsigned short | 16 |
| OPTE policy context prefix | unsigned long long | 64 |

Total: `176 bits`. `tests/test_kernel.py::test_qom_compact_payload_is_exact_176_bit_struct` unpacks the emitted bytes and validates the field boundaries.

## Qiskit Bridge

`examples/qiskit_bridge.py` is an optional integration example for reviewers who want to see the control plane wrap around a standard quantum simulation framework. It:

1. Builds a 4-qubit GHZ circuit.
2. Runs it on a Qiskit Aer simulator with thermal relaxation and depolarizing noise.
3. Optionally injects coherent crosstalk with parasitic `RXX`/`RZZ` operations between adjacent virtual qubits.
4. Applies monitor-controlled Qiskit noise scaling, weak-measurement efficiency, and leakage-lambda telemetry degradation.
5. Converts noisy shot counts into expectation-value telemetry.
6. Maps that telemetry into the AEGIS 5-variable environment grid and `NodeTelemetry` inputs.
7. Emits normal AEGIS cycle outputs, including governance states, `.QOM` payload bits, and Merkle lineage.

The bridge is intentionally optional so the core repository remains runnable with the Python standard library.

When the live monitor is running, the Qiskit bridge is also exposed through local HTTP endpoints:

- `POST /api/qiskit/run?cycles=6&shots=2048&seed=2026&noise_scale=1.0&crosstalk_inject=false&leakage_lambda=0.0&measurement_efficiency=0.82`: runs the optional Qiskit Aer bridge and writes `monitor_snapshots/qiskit_bridge_*.json`.
- `POST /api/qiskit/stop`: requests cancellation of the Qiskit bridge loop without stopping the live monitor, report exports, or local server.
- `GET /api/qiskit/latest`: returns the newest bridge or imported bridge artifact.
- `GET /api/qiskit/export`: returns the current bridge artifact for dashboard download.
- `POST /api/qiskit/import`: accepts a prior bridge JSON payload, stores it as `monitor_snapshots/qiskit_import_*.json`, and loads it into the monitor.

## IBM Quantum Bridge

`examples/ibm_bridge.py` is an optional bridge for IBM Quantum Runtime. It defaults to a local fake IBM backend so reviewers can validate the mapping without waiting in a cloud queue. Real hardware execution is explicit with `--real`.

Setup and operational cautions are documented in `docs/ibm_quantum_setup.md`.

Local fake-backend smoke test:

`python examples/ibm_bridge.py --shots 256 --output ibm_bridge_fake_result.json`

Real hardware, when credentials are configured locally:

`python examples/ibm_bridge.py --real --shots 1024 --output ibm_bridge_result.json`

Session-style batch loop, local fake backend smoke test:

`python examples/session_batch_loop.py --batches 3 --shots 128 --output ibm_session_batch_loop_fake_smoke.json`

Session-style batch loop, real hardware:

`python examples/session_batch_loop.py --real --backend ibm_marrakesh --batches 3 --shots 256 --output ibm_session_batch_loop.json`

The session-style loop is the current near-real-time bridge pattern: it does not control the QPU during a circuit, but it keeps runtime resources warm and runs AEGIS immediately after each returned batch. If the account or backend does not allow a Runtime Session, the script falls back to normal IBM jobs and records the fallback reason in the output JSON.

Ready-to-run real backend validation commands are maintained in [`docs/adaptive_validation_plan.md`](docs/adaptive_validation_plan.md). Those commands spend IBM Quantum runtime and should be executed deliberately.

## Algorithmic Grounding

Several AEGIS terms are project-specific names for established engineering patterns:

- **Meaning-based compression:** modeled as lossy high-utility telemetry filtering, where low-value floating-point tails and repeated sensor noise are truncated before archival. This follows common industrial telemetry compression and lossy signal-compression practice.
- **Weighted Byzantine quorum isolation:** grounded in Byzantine fault-tolerant distributed systems. AEGIS keeps the `f < n/3` mindset, requires a minimum physical node count, and weights candidate vectors by trust before medoid/outlier filtering.
- **Wrapped-delta phase unwrapping:** implemented as `wrap_pi(delta) = ((delta + pi) mod 2pi) - pi`, accumulated into a continuous track. This is aligned with PLL-style phase tracking and Itoh-style phase-unwrapping logic.
- **Unsafe-output prevention efficiency:** a reliability metric over unsafe-output opportunities, not a claim that software removes physical noise. It measures how often the control plane prevents unsafe data from reaching the output or ledger.

## JSON Export Layout

The monitor and runner export JSON payloads containing:

- `projection_validation`: public targets, stretch targets, theoretical cascade boundaries
- `observed_cascade_efficiency_estimates`: Monte Carlo-derived eta estimates and variance reductions
- `advanced_performance_report`: baseline, storm, adversarial, and fail-closed summaries
- `deterministic_suite`: scenario-by-scenario kernel cycle results
- `monte_carlo`: UOP, USR, continuity, integrity-preserved, and tier metrics
- `scope`: canonical runtime loop and active architecture module descriptions

Each live cycle result includes governance states, kappa vector mean, multiplicative trust channels, continuity gates, unsafe-output fields, Merkle root, block hash, `.QOM` payload, OPTE hash, hardware register diagnostics, secure enclave vault state, cryogenic scheduler output, reviewer telemetry, handoff slack, key lineage, energy efficiency, relativistic clock compensation, ZNE tuning, and RTOS scheduler diagnostics.

## Discoverability Topics

Suggested topics:

`quantum-sre`, `site-reliability`, `control-plane`, `telemetry-simulation`, `fault-tolerance`, `distributed-systems`, `zero-trust`, `quantum-computing`, `sre`, `observability`, `monte-carlo-simulation`, `byzantine-fault-tolerance`, `error-mitigation`, `merkle-tree`, `cryptographic-ledger`, `python`, `standard-library`, `simulation-framework`, `reliability-engineering`, `hardware-observability`

## References

- Lamport, Shostak, and Pease, "The Byzantine Generals Problem," ACM Transactions on Programming Languages and Systems, 1982.
- Pease, Shostak, and Lamport, "Reaching Agreement in the Presence of Faults," Journal of the ACM, 1980.
- Itoh, "Analysis of the phase unwrapping algorithm," Applied Optics, 1982.
- Best, "Phase-Locked Loops: Design, Simulation, and Applications."
- Cover and Thomas, "Elements of Information Theory."
- Qiskit and Qiskit Aer project documentation for circuit simulation and noise-model integration.

## Contact

For technical review, collaboration, licensing questions, or implementation discussion, open a GitHub Issue on this repository or contact the author through the GitHub profile:

`@sticktapemedical-byte`

## License

This repository is distributed under the noncommercial terms in `LICENSE`. Commercial use requires a separate written commercial license; see `COMMERCIAL_LICENSE.md`.
