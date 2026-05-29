# DD-Style Idle Echo Circuit Definitions

These circuits are used by `examples/dynamical_decoupling_insertion.py`. They are ordinary Qiskit gate/delay circuits submitted through IBM Runtime when backend compilation supports them. They are not pulse-level schedules and do not claim intrinsic coherence extension.

All arms use a one-qubit phase-survival template:

```text
h q[0]
<sequence-specific idle/echo block>
h q[0]
measure q[0] -> c[0]
```

The current real campaign used `delay_us = 50.0` and `shots = 512` per arm on `ibm_marrakesh`.

| Sequence | Inserted block | Public claim boundary |
| --- | --- | --- |
| `none` | `delay(50 us)` | Baseline idle-window survival for the submitted workload. |
| `xx` | `delay(25 us); x; delay(25 us); x` | Simple echo-style comparison arm. |
| `xy4` | four `delay(12.5 us)` windows interleaved with `x; y; x; y` | Echo-style comparison arm, not calibrated pulse DD. |
| `cpmg` | same compiled gate pattern as current `xy4` placeholder in the harness | Placeholder comparison arm until a calibrated CPMG mapping is added. |

The 2026-05-29 result selected `xy4` for that single tested workload/run. Stronger claims require repeats across delay values, backends, and calibration windows.
