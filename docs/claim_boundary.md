# Claim Boundary

AEGIS is an experimental quantum workload reliability framework for returned QPU outputs and probabilistic telemetry. It is designed to test whether adaptive selection, classical governance, fail-closed rules, compact metadata, and lineage can improve accepted-result quality and resource efficiency under tested conditions.

## Safe Current Claim

AEGIS ingests simulator outputs or real IBM Quantum count histograms, maps them into telemetry, applies classical governance, emits `.QOM` metadata, and writes Merkle lineage over returned job outputs.

## Improved Claim Supported By Current Harnesses

AEGIS can reject, warn on, or fail-close lower-quality returned outputs and can use probe results to select later execution paths such as backend, layout, and mitigation policy.

## Claim To Earn With More Controlled Evidence

AEGIS-selected control policies improved measured coherence-sensitive workload survival under tested conditions.

This wording is intentionally narrower than saying the system improves physical coherence.

## Do Not Claim

- AEGIS improves intrinsic qubit coherence.
- AEGIS changes chip materials, device physics, refrigerator behavior, or hardware calibration.
- AEGIS solves decoherence.
- AEGIS replaces quantum error correction.
- AEGIS controls a public IBM QPU while a circuit is actively running, except where an explicit IBM-supported dynamic-circuit feature is used and reported as such.
- AEGIS is a universal physical quantum operating system.

## Future Claim Class Only After Stronger Evidence

Any claim about changing effective coherence behavior must be reserved for future controlled results with matched baselines, higher shot counts, confidence intervals, and negative-result handling.

Until then, use:

> AEGIS-selected control policies improved measured coherence-sensitive workload survival under tested conditions.
