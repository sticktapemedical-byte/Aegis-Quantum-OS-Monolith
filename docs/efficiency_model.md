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
- mean accepted quality.

## Acceptance Rule

The current utility accepts records that satisfy available quality and lineage fields:

- continuity gate or raw AEGIS gate when present,
- `q_conf` threshold when present,
- GHZ quality threshold when present,
- `.QOM` and Merkle lineage for generic records.

## Latest Sanitized Rollup

From `docs/validation/efficiency_summary.json`:

- artifacts: `28`,
- tracked shots: `64,640`,
- accepted artifacts: `18`,
- rerun rate: `35.71%`,
- shots per accepted artifact: `3,591.11`.

These figures mix heterogeneous validation artifacts and should be interpreted as artifact accounting, not as a single homogeneous QPU benchmark.

