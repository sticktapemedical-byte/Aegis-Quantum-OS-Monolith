# AEGIS Master IBM Quantum Validation Report

Generated from real IBM Quantum Runtime jobs executed on May 28, 2026.

## Scope Boundary

These results summarize real IBM Quantum backend jobs whose raw hardware counts were ingested by the AEGIS site reliability control-plane simulation framework. AEGIS performs classical post-processing, telemetry mapping, continuity/setpoint governance, compact 176-bit `.QOM` frame generation, and Merkle lineage logging over returned count histograms.

They are not presented as a broad benchmark of IBM hardware, a device calibration result, or evidence that AEGIS changes physical quantum noise. The hardware executes the circuits; AEGIS governs and records the returned data path.

## Executive Rollup

| Category | Value |
|---|---:|
| Real backend jobs represented | 11 |
| IBM backends used | `ibm_marrakesh`, `ibm_kingston`, `ibm_fez` |
| Total shots represented | 15,232 |
| Multi-backend GHZ devices tested | 3 |
| Corrected setpoint validations | 15 / 15 |
| Compact `.QOM` frame width | 176 bits |

## Statistical Rigor Note

This is an early end-to-end validation set. The 11 hardware jobs prove that the bridge can execute, ingest, score, serialize, and ledger real backend results. They do not establish device-level performance claims.

Most individual runs use 128 to 512 shots, with one 1024-shot GHZ run, one 4096-shot GHZ run, two 1280-shot phase-sweep jobs, and one 5120-shot high-resolution setpoint sweep. Stronger future studies should add:

- more repeated runs per backend and condition,
- higher shot counts where account limits permit,
- confidence intervals for GHZ population and setpoint error,
- contemporaneous backend calibration snapshots,
- separated analysis for readout error, gate error, queue latency, and control-plane decisions.

## Master Validation Ledger

| Test | Backend | Job ID | Shots | Primary Result | AEGIS Result | Purpose |
|---|---|---:|---:|---:|---|---|
| Initial 4-qubit GHZ hardware ingestion | `ibm_marrakesh` | `d8cf0vr8ch0s738uppq0` | 1024 | GHZ population `94.24%`, raw non-GHZ `5.76%` | Continuity passed, `NORMAL` | First real hardware ingestion proof for GHZ counts, `.QOM`, and Merkle lineage. |
| Same-backend repeatability | `ibm_marrakesh` | `d8cf7cj8ch0s738uq3qg` | 512 | GHZ population `96.09%`, raw non-GHZ `3.91%` | Continuity passed, `NORMAL` | Same backend comparison with lower shot count. |
| High-shot GHZ stability | `ibm_marrakesh` | `d8cfjoijki0s73ar75bg` | 4096 | GHZ population `95.19%`, raw non-GHZ `4.81%` | Continuity passed, `NORMAL` | Higher-shot GHZ run for a stronger single-condition estimate. |
| Idle-delay stress | `ibm_marrakesh` | `d8cf7n47avuc73dqtus0` | 128 | GHZ population `95.31%`, raw non-GHZ `4.69%` | Continuity passed, `NORMAL` | Added a 1 ms declared circuit delay before the CNOT cascade to test delay-stress ingestion. |
| Cross-device topology comparison | `ibm_kingston` | `d8cf7r2jki0s73ar6gv0` | 256 | GHZ population `92.58%`, raw non-GHZ `7.42%` | Continuity passed, `NORMAL` | Confirmed the bridge can ingest a different IBM backend. |
| Cross-device topology comparison | `ibm_fez` | `d8cf8n38ch0s738uq6vg` | 256 | GHZ population `83.59%`, raw non-GHZ `16.41%` | Continuity passed, `NORMAL` | Added a second non-marrakesh chip to compare device variation. |
| Fast single-qubit coherence/readout pass | `ibm_marrakesh` | `d8cfb5j8ch0s738uqcd0` | 256 | `P(0)=53.13%`, `P(1)=46.88%`, phase estimate `1.5083 rad` | Continuity passed, `NORMAL` | Lightweight single-qubit physical data stream for fast ingestion validation. |
| Long-form continuous phase sweep | `ibm_marrakesh` | `d8cfc8ijki0s73ar6ri0` | 1280 | Mean `q_conf=0.94838` | Failed closed after unannounced phase changes | Proved the kernel does not silently accept discontinuous trajectory jumps as valid continuity. |
| Corrected commanded setpoint sweep | `ibm_marrakesh` | `d8cfd4ijki0s73ar6tkg` | 640 | Setpoints `5/5`, mean abs error `0.0063` | `NORMAL`; no anchor dispute | Reframed each phase as an intentional calibration target with a fresh anchor window. |
| Corrected full-capacity setpoint sweep | `ibm_marrakesh` | `d8cfdvqjki0s73ar6uog` | 1280 | Setpoints `5/5`, mean abs error `0.0219` | `NORMAL`; final `.QOM` generated | Fuller corrected setpoint run with 256 shots per phase. |
| High-shot commanded setpoint sweep | `ibm_marrakesh` | `d8cfk538amns73bjg5gg` | 5120 | Setpoints `5/5`, mean abs error `0.0043` | `NORMAL`; final `.QOM` generated | Higher-resolution commanded setpoint validation with 1024 shots per phase. |

## Highlights

- Multi-backend GHZ ingestion completed across `ibm_marrakesh`, `ibm_kingston`, and `ibm_fez`.
- All GHZ bridge runs generated valid 176-bit `.QOM` metadata frames and Merkle lineage roots.
- The 1 ms idle-delay GHZ stress run stayed in `NORMAL` governance and passed continuity.
- The first continuous phase sweep intentionally failed closed under apparent anchor drift, validating fail-closed behavior.
- The corrected commanded-setpoint sweeps passed all setpoint checks after the test declared each phase as an intentional calibration target.
- The 4096-shot GHZ run produced `95.19%` target-state population and passed continuity under `NORMAL` governance.
- The 1024-shot-per-phase setpoint sweep passed `5/5` commanded setpoints with mean absolute error `0.0043`.

## Technical Breakdown

1. IBM Quantum Runtime returned raw bitstring count histograms from real backend jobs.
2. GHZ tests classified target-state mass as `counts(0000) + counts(1111)`.
3. Single-qubit phase tests compared observed `P(1)` against the commanded model `P(1)=sin^2(theta/2)`.
4. AEGIS mapped counts into telemetry lanes with phase estimates, environment pressure, latency, and trust inputs.
5. The kernel executed projection, wrapped-delta phase unwrapping, quorum/anchor checks, governance bitmask evaluation, compact `.QOM` emission, and Merkle commit.
6. Continuous trajectory tests and commanded setpoint tests are intentionally separated: continuity gates are strict trajectory-corridor checks, while setpoint validation checks whether declared calibration targets were matched.
7. The compact `.QOM` payload is implemented in `AegisContinuityKernel.emit_compact_qom_payload(...)` using `struct.pack(">IHHHHHQ", ...)`, producing exactly 22 bytes / 176 bits. `tests/test_kernel.py::test_qom_compact_payload_is_exact_176_bit_struct` unpacks the emitted bytes and validates the field boundaries.

## Local Artifacts

Raw JSON outputs and generated PDFs remain on the local workstation and are intentionally ignored by Git. This keeps the public repository clean while preserving forensic records locally.
