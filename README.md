# AEGIS Quantum Workload Reliability Framework

AEGIS is an experimental quantum workload reliability framework for evaluating QPU outputs, selecting execution paths, preserving result lineage, and measuring accepted-result quality under noisy cloud-QPU conditions.

AEGIS does **not** claim to improve intrinsic qubit coherence, alter hardware physics, solve quantum noise, replace quantum error correction, or control public IBM Quantum hardware while a circuit is actively running. This repository evaluates whether adaptive selection and classical governance can improve accepted workload quality, coherence-sensitive workload survival metrics, and resource cost per accepted result under tested conditions.

## What This Is / What This Is Not

| This repository is | This repository is not |
| --- | --- |
| A Python reliability framework around probabilistic telemetry and QPU output histograms. | A physical quantum operating system or deployed hardware controller. |
| A classical post-processing and workload-governance layer with optional IBM Quantum Runtime bridges. | A claim that software physically removes or suppresses quantum noise. |
| A test harness for accepted/rejected quality gates, backend selection, mitigation selection, `.QOM` metadata, and Merkle lineage. | Evidence of intrinsic device-level coherence improvement. |
| A noncommercial research/portfolio codebase with commercial licensing reserved separately. | A permission grant for commercial platform integration. |

## Current Execution Model

1. IBM Quantum Runtime or a simulator executes a circuit.
2. AEGIS ingests returned count histograms after the job completes.
3. AEGIS evaluates quality, trust, governance, `.QOM` metadata, and lineage.
4. Adaptive scripts can use those results to choose later workloads, backends, layouts, or mitigation policies.

This is **not real-time QPU control during a running circuit**. Dynamic-circuit and DD-style harnesses are included where supported, but public claims remain limited to observed workload outputs and later workload selection.

## Terminology

**Q-SRE** means applying classical Site Reliability Engineering patterns, such as observability, fail-closed behavior, quality gates, and lineage, to noisy probabilistic systems.

**`.QOM`** means **Quality Orchestration Metadata**. It is a compact 176-bit metadata frame carrying phase, confidence/coherence proxy, lifecycle, trust, risk/backaction proxy, governance, and policy context. It is not a network TLD and not a claim of quantum transport.

For technical review, the safest name is **Aegis Continuity Kernel** or **Probabilistic SRE Control Plane**.

## Repository Map

| File or directory | Purpose |
| --- | --- |
| `aegis_kernel.py` | Core governance, trust, `.QOM`, Merkle lineage, and fail-closed logic. |
| `aegis_os.py` | Terminal runner and reviewer-mode output. |
| `aegis_monitor.py` | Local HTTP monitor. |
| `examples/` | IBM/Qiskit bridges, selectors, mitigation, DD-style, dynamic-circuit, holdout, ablation, and report scripts. |
| `tests/` | Unit and regression tests. |
| `circuits/` | Exact circuit specs used for public validation. |
| `schemas/` | Lightweight validation artifact schemas. |
| `docs/validation/` | Sanitized IBM validation artifacts, reports, and generated summaries. |

## Key Documentation

- [Claim Boundary](docs/claim_boundary.md)
- [Implementation Status](docs/implementation_status.md)
- [Validation Plan](docs/validation_plan.md)
- [IBM QPU Test Plan](docs/ibm_qpu_test_plan.md)
- [Policy Catalog](docs/policy_catalog.md)
- [DD-Style Circuit Definitions](docs/dd_style_circuit_definitions.md)
- [Schemas](docs/schemas.md)
- [Efficiency Model](docs/efficiency_model.md)
- [Publication Checklist](docs/publication_checklist.md)
- [Runtime Boundaries](docs/runtime_boundaries.md)
- [Architecture Diagram](docs/architecture.svg)
- [Sample Reviewer Output](docs/sample_reviewer_output.json)
- [Roadmap](ROADMAP.md)
- [Assumptions](ASSUMPTIONS.md)
- [Validation Notes](VALIDATION.md)

## Real IBM Quantum Results

The latest campaign report is here:

- [AEGIS Adaptive IBM Backend Campaign - 2026-05-29](docs/validation/AEGIS_Adaptive_IBM_Backend_Campaign_2026-05-29.md)

Current public-safe validation vault:

- Sanitized artifacts represented: `28`
- Total tracked shots in sanitized summaries: `71,296`
- Tests passing locally: `28`
- `.QOM` compact payload width: `176 bits`

Campaign highlights:

- Accepted/rejected quality split on `ibm_marrakesh`: accepted mean GHZ `95.25%`, all mean `94.88%`, rejected mean `93.05%`.
- Readout mitigation repeat on `ibm_marrakesh`: mean raw GHZ `95.77%`, mean mitigated GHZ `97.50%`, uplift `+1.73 percentage points`.
- Adaptive backend selector: selected `ibm_marrakesh` over `ibm_kingston`; committed GHZ `95.70%`.
- DD-style idle echo harness: selected `xy4`; survival `70.12%` vs no-DD-style arm `33.59%` in one workload/run; repeat testing is still required.
- Dynamic-circuit governance: real `ibm_marrakesh` dynamic-circuit job completed.
- Negative/inconclusive results are preserved: delay-ramp monotonic degradation was not observed, and the coherence-controller delay fit did not expose a decay curve.

These are returned-output and workload-selection results, not claims of changing the hardware physics.

## Quick Start

Run the standard simulation:

```powershell
python aegis_os.py
```

Run reviewer mode:

```powershell
python aegis_os.py --reviewer-mode --output aegis_os_report.json
```

Run all tests:

```powershell
python -m pytest tests
```

Run optional IBM fake-backend smoke test:

```powershell
python examples/ibm_bridge.py --shots 256 --output ibm_bridge_fake_result.json
```

Real IBM jobs require local credentials and explicit `--real` flags. See [IBM QPU Test Plan](docs/ibm_qpu_test_plan.md).

## License And Commercial Use

This repository is published for noncommercial research, evaluation, education, benchmarking, and technical review under `LICENSE`.

Commercial use is not included in the public license. Production deployment, proprietary product integration, hosted service use, paid consulting delivery, internal enterprise platform integration, commercial redistribution, or use of the project identity in a commercial offer requires a separate written commercial license. See `COMMERCIAL_LICENSE.md`.

## Support

- [Support Aegis Reliability Lab on Buy Me a Coffee](https://buymeacoffee.com/aegisqsrelab)

## Contact

For technical review, collaboration, licensing questions, or implementation discussion, open a GitHub Issue on this repository or contact the author through the GitHub profile.
