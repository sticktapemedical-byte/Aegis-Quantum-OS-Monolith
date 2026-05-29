# IBM QPU Test Plan

## Current Scope

AEGIS uses IBM Quantum Runtime to submit circuits, receive count histograms, and process returned outputs after completion. Real jobs are only submitted when a command includes `--real`.

## Credential Safety

- Keep IBM credentials in local `.env` or Qiskit local account storage.
- Do not commit `.env`, tokens, local account files, or private account identifiers.
- Use sanitized artifacts for public reporting.

## Recommended Test Order

Run lower-cost tests first:

```powershell
python examples/ibm_backend_discovery.py --output ibm_backend_inventory.json
python examples/accepted_vs_rejected.py --real --backend ibm_marrakesh --batches 30 --shots 256 --accept-threshold 0.94 --output accepted_vs_rejected.json
python examples/readout_mitigation_repeat.py --real --backend ibm_marrakesh --repeats 10 --ghz-shots 1024 --calibration-shots 256 --output readout_mitigation_repeat.json
python examples/adaptive_backend_selector.py --real --backends ibm_marrakesh,ibm_kingston --probe-shots 256 --commit-shots 1024 --output adaptive_backend_selector.json
python examples/adaptive_mitigation_selector.py --real --backend ibm_marrakesh --ghz-shots 1024 --calibration-shots 256 --output adaptive_mitigation_selector.json
python examples/dynamical_decoupling_insertion.py --real --backend ibm_marrakesh --shots 512 --delay-us 50 --output dynamical_decoupling_insertion.json
python examples/dynamic_circuit_governance.py --real --backend ibm_marrakesh --shots 256 --output dynamic_circuit_governance.json
```

Avoid heavily queued backends unless the test explicitly needs cross-device coverage.

## Current Real Campaign Summary

See [AEGIS Adaptive IBM Backend Campaign - 2026-05-29](validation/AEGIS_Adaptive_IBM_Backend_Campaign_2026-05-29.md).

The latest campaign included:

- accepted/rejected split,
- delay-ramp test,
- readout mitigation repeat,
- probe-then-commit,
- backend selector,
- layout selector,
- mitigation selector,
- coherence-controller delay-ramp,
- DD-style idle echo insertion,
- dynamic-circuit governance,
- calibration campaign policy record,
- pulse-control policy register.

## Backend Feature Notes

| Feature | IBM Cloud support expectation |
| --- | --- |
| Standard circuits and counts | Supported. |
| Runtime Sessions | Not available on current open plan; code falls back to job mode. |
| Dynamic circuits | Supported on tested `ibm_marrakesh` path for the included template. |
| DD-style echo gates | Implemented as normal gates/delays where compilation supports them. |
| Full pulse-level control | Not claimed for public IBM Runtime. |
| RB/T1/T2/tomography campaign | Requires dedicated shot budget and protocol. |

