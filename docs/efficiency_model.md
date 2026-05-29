# Efficiency Model

AEGIS measures resource efficiency over accepted returned outputs. This is not a refrigerator power measurement and not a claim that the software reduces base cryogenic load.

## Implemented Metrics

Implemented in `aegis_efficiency.py`:

- accepted result count,
- rerun count,
- rerun rate,
- total shots,
- total jobs,
- shots per accepted result,
- jobs per accepted result,
- mean accepted quality for homogeneous artifact sets.

For mixed validation vaults, use split quality fields in `docs/validation/ablation_workflow.json` instead of treating every artifact as one interchangeable score.

## Acceptance Rule

The current utility accepts records that satisfy available quality and lineage fields:

- continuity gate or raw AEGIS gate when present,
- `q_conf` threshold when present,
- GHZ quality threshold when present,
- `.QOM` and Merkle lineage for generic records.

## Latest Sanitized Rollup

From `docs/validation/efficiency_summary.json`:

- artifacts: `32`,
- tracked shots: `71,424`,
- accepted artifacts: `25`,
- rerun rate: `21.88%`,
- shots per accepted artifact: `2,856.96`.

These figures mix heterogeneous validation artifacts and should be interpreted as artifact accounting, not as a single homogeneous QPU benchmark.
