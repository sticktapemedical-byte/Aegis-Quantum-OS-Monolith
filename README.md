# Aegis Quantum OS Monolith

## Executive Summary

Aegis Quantum OS Monolith is a full-stack Quantum Site Reliability Engineering (Q-SRE) control-plane simulation for mediating probabilistic hardware interfaces. It models how classical reliability engineering patterns can observe, score, gate, and preserve useful operational continuity across noisy telemetry streams, adversarial node behavior, cryptographic lineage events, and hardware-inspired timing constraints.

The project is written for infrastructure engineers, site reliability engineers, distributed systems reviewers, security auditors, and hardware observability teams who need a runnable demonstration of a continuity kernel, live telemetry monitor, stress injection deck, and forensic artifact exporter.

The simulation does not claim to modify physical qubits or bypass physics. It demonstrates a software control-plane model for unsafe-output prevention, trust scoring, fail-closed governance, telemetry fusion, and auditability around probabilistic or high-entropy systems.

## Discoverability Keywords

Suggested GitHub topics:

`quantum-computing`, `site-reliability-engineering`, `sre`, `distributed-systems`, `observability`, `telemetry`, `fault-tolerance`, `byzantine-fault-tolerance`, `monte-carlo-simulation`, `control-plane`, `simulation-framework`, `reliability-engineering`, `error-mitigation`, `cryptographic-ledger`, `merkle-tree`, `zero-trust`, `python`, `standard-library`, `infrastructure`, `hardware-observability`

## Technical Metrics

The current simulation and monitor track these benchmark classes:

- Unsafe-output prevention efficiency: measured as unsafe outputs prevented divided by unsafe-output opportunities.
- Public v1 UOP target: 0.9949.
- Systemic stretch UOP target: 0.9990.
- Theoretical cascade boundary target: 0.99925.
- Unnecessary shutdown rate target: below 0.05.
- Meaningful Continuity: reported as both raw lifespan multiplier and normalized corridor health.
- Compression ratio: reviewer telemetry reports a 14.2x data compression ratio.
- Observed cascade reductions:
  - Weighted Byzantine filtering estimates variance reduction on corrupted node vectors.
  - Taylor-domain projection estimates timing-jitter reduction.
  - Riemann phase unwrapping estimates wrapped-to-unwrapped acceleration variance suppression.
- Uptime-style scenario reporting: the terminal suite models baseline, storm, adversarial, fail-closed, and recovery-validation paths.

## Architecture Overview

### Layer 4: Network Mesh Layer

The mesh layer models decentralized data transport, live disruption injection, `.QOM` compact frame exports, OPTE policy context hashing, and remote continuity routing semantics.

### Layer 3: Regional Hub Nodes

Regional nodes model weighted quorum voting, node quarantine, rolling anchor verification, Merkle lineage, forensic certificates, and multi-branch key mutation traces.

### Layer 2: Acceleration Tier

The acceleration tier models math offload for Taylor-domain kinetic phase normalization, Riemann manifold phase unwrapping, weighted vector fusion, Monte Carlo cascade efficiency estimation, and reviewer-mode telemetry metrics.

### Layer 1: Register Abstraction

The register abstraction maps low-level gating concepts into simulated FPGA/ASIC-style diagnostics:

- `G(t)` boundary gating.
- Hardware register handoff slack.
- O-quantization timing windows.
- Relativistic timestamp compensation.
- RTOS queue depth and lockhold latency.
- Cryogenic thermal scheduling and joule-density cost.

## Deployment Instructions

### Prerequisites

- Windows, macOS, or Linux.
- Python 3.10 or newer recommended.
- Git recommended for repository tracking.

### Zero Dependencies

The core simulation and local monitor use only the Python standard library. No package installation is required.

### Run The Terminal Simulation

From this repository folder:

`python aegis_os.py`

Reviewer-mode terminal output:

`python aegis_os.py --reviewer-mode`

### Run The Live Monitor

From this repository folder:

`python aegis_monitor.py --host 127.0.0.1 --port 8765`

Then open:

`http://127.0.0.1:8765`

PowerShell helper scripts are also provided in `scripts/`.

## Live Monitor Controls

The live monitor includes:

- Start/stop live runtime feed.
- Stress injection dropdown.
- Spoofed-node percentage slider.
- Kp and Kd damping sliders.
- Omega drive control.
- ZNE lambda control.
- Backaction threshold control.
- Anchor decay lambda control.
- Innovation eta control.
- Reviewer-mode toggle.
- RB calibration interleave toggle.
- Relativistic timestamp compensation toggle.
- Hard-abort reset.
- Recovery-validate initialization.
- `.QOM` hex export.
- Forensic certificate export.
- Snapshot and full report JSON export.

## Repository Assets

- `aegis_kernel.py`: core `AegisContinuityKernel`, metrics, governance, Monte Carlo, ledger, and telemetry logic.
- `aegis_monitor.py`: local browser monitor and API server.
- `aegis_os.py`: terminal-oriented simulation runner.
- `AEGIS_MISSION_AND_ARCHITECTURE.md`: extended technical architecture notes.
- `artifacts/`: small checked-in sample outputs.
- `scripts/`: PowerShell launch helpers.
- `LICENSE`: non-commercial license reference.

## Artifact Locations

Runtime-generated monitor artifacts are written to:

`monitor_snapshots/`

Browser downloads may also appear in the user Downloads folder depending on browser settings.

## JSON Export Layout

The monitor exports JSON payloads containing:

- `projection_validation`: public targets, stretch targets, theoretical cascade boundaries.
- `observed_cascade_efficiency_estimates`: Monte Carlo-derived eta estimates and variance reductions.
- `advanced_performance_report`: tiered baseline, storm, and adversarial summaries.
- `deterministic_suite`: scenario-by-scenario kernel cycle results.
- `monte_carlo`: UOP, USR, continuity, integrity-preserved, and tier metrics.
- `scope`: canonical runtime loop and active architecture module descriptions.

Each live cycle result includes:

- governance mask and active states
- kappa vector mean
- multiplicative trust channels
- continuity gates
- unsafe-output opportunity/prevention fields
- Merkle root and block hash
- `.QOM` compact payload
- OPTE policy context hash
- hardware register diagnostics
- secure enclave vault state
- cryogenic scheduler output
- reviewer telemetry
- hardware handoff slack
- key mutation lineage
- energy efficiency
- relativistic clock compensation
- ZNE tuning
- RTOS scheduler diagnostics

## License

This repository is distributed under the license terms in `LICENSE`.
