# AEGIS Quantum Workload Reliability Validation Plan

## Purpose

This plan defines how AEGIS should be evaluated as a returned-output governance and adaptive workload-selection framework.

The goal is to move from:

```text
run circuit -> receive counts -> score/gate/log output
```

to:

```text
probe candidate policies -> score returned outputs -> select the next workload path -> compare against fixed baselines -> preserve lineage
```

## Required Evidence For Serious Review

Every public validation report should include:

- raw histograms,
- job IDs,
- exact circuits or circuit hashes,
- shot counts,
- backend names,
- Qiskit and runtime versions,
- confidence intervals,
- raw-vs-governed comparisons,
- negative-result handling,
- blind holdout split,
- ablation results,
- `.QOM` payloads,
- Merkle roots,
- claim-boundary notes.

## Validation Stages

| Stage | Meaning | Current status |
| --- | --- | --- |
| Current returned-output governance | Ingest counts, score, gate, serialize, and log lineage. | Implemented with IBM results. |
| Quality gate | Show accepted outputs are better than rejected/all outputs. | Implemented and run on `ibm_marrakesh`. |
| Adaptive selector | Use probe outputs to choose later backend/layout/mitigation decisions. | Implemented and run for backend/mitigation/layout. |
| Control-policy validation | Compare selected policies against fixed baselines under the same calibration window. | Partially implemented with DD-style harness; needs broader repeats. |
| Final validation target | Show selected policies improve measured coherence-sensitive workload survival under tested conditions. | Not broadly earned yet. |

## Negative Result Policy

Negative or inconclusive results must remain in the artifact vault. The 2026-05-29 delay-ramp tests did not show monotonic degradation, so they are reported as inconclusive for that degradation claim.

