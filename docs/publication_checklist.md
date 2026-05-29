# AEGIS Publication Checklist

Use this checklist before publishing or submitting a validation report.

- State the current execution model: AEGIS governs returned IBM Quantum outputs and can select later workloads.
- Do not claim intrinsic T1/T2 improvement, physical noise suppression, universal QPU control, or real-time control during an active circuit.
- Include exact circuit specs or hashes.
- Include backend names, job IDs, shot counts, timestamps, Qiskit versions, `.QOM` payloads, and Merkle roots.
- Include `docs/validation/threshold_freeze.json` and state that thresholds were frozen before holdout interpretation.
- Include train/holdout split output from `examples/blind_holdout.py`.
- Include ablation output from `examples/ablation_workflow.py`.
- Include resource accounting from `examples/efficiency_report.py`.
- Include report artifacts from `examples/generate_validation_report.py`.
- Label all IBM hardware results as real returned-output ingestion and governance results.
- Label all fake/synthetic runs clearly as fake or synthetic.
