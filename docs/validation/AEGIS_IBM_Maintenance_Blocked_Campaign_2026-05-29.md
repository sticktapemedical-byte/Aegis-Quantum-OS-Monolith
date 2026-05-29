# AEGIS IBM Maintenance-Blocked Campaign - 2026-05-29

## Status

IBM Quantum Cloud/QPU workload pages were unavailable to the operator, and local backend discovery timed out before returning backend inventory. This is recorded as a campaign availability block, not a negative AEGIS result.

## Completed During Block

| Item | Status | Evidence |
| --- | --- | --- |
| DD repeat campaign wrapper | Implemented and smoke-tested locally | `examples/dd_repeat_campaign.py`, `dd_repeat_campaign.json` |
| Negative regression suite wrapper | Implemented and smoke-tested locally | `examples/negative_regression_suite.py`, `negative_regression_suite.json` |
| QAOA bridge | Implemented and smoke-tested locally | `examples/qaoa_bridge.py`, `qaoa_bridge.json` |
| Maintenance block artifact | Generated | `ibm_maintenance_blocked_campaign.json` |

## Real Backend Queue

Run these when IBM Quantum workloads are visible again:

```powershell
python examples/dd_repeat_campaign.py --real --backend ibm_marrakesh --repeats 10 --shots 128 --delays-us 25,50,100 --output dd_repeat_campaign.json
python examples/adaptive_backend_selector.py --real --backends ibm_marrakesh,ibm_kingston,ibm_fez --probe-shots 128 --commit-shots 512 --output adaptive_backend_selector.json
python examples/delay_ramp.py --real --backend ibm_marrakesh --shots 512 --delays-ms 0,5,10,20 --output delay_ramp.json
python examples/adaptive_coherence_controller.py --real --backend ibm_marrakesh --shots 512 --delays-ms 0,5,10,20 --output adaptive_coherence_controller.json
python examples/readout_mitigation_repeat.py --real --backend ibm_marrakesh --repeats 10 --ghz-shots 512 --calibration-shots 128 --output readout_mitigation_repeat.json
python examples/qaoa_bridge.py --real --backend ibm_marrakesh --shots 512 --output qaoa_bridge.json
python examples/negative_regression_suite.py --real --backends ibm_marrakesh,ibm_kingston,ibm_fez --shots 128 --delays-ms 0,5,10 --output negative_regression_suite.json
```

## Claim Boundary

This document is operational bookkeeping. It does not add QPU evidence. It proves that the missing campaign pieces now have executable wrappers and public artifacts ready for real-backend collection.
