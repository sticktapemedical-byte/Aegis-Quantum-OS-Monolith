from __future__ import annotations

import argparse
import json
from pathlib import Path

from examples.ibm_bridge import require_runtime


def discover_backends(channel: str) -> dict[str, object]:
    qiskit_runtime_service, _, _ = require_runtime()
    service = qiskit_runtime_service(channel=channel)
    rows = []
    for backend in service.backends(simulator=False, operational=True):
        status = backend.status()
        rows.append(
            {
                "name": backend.name,
                "num_qubits": getattr(backend, "num_qubits", None),
                "pending_jobs": status.pending_jobs,
                "operational": status.operational,
                "status_msg": status.status_msg,
            }
        )
    rows.sort(key=lambda item: (item["pending_jobs"], item["name"]))
    return {"channel": channel, "backends": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover accessible IBM Quantum backends for AEGIS.")
    parser.add_argument("--channel", default="ibm_quantum_platform")
    parser.add_argument("--output", type=Path, default=Path("ibm_backend_inventory.json"))
    args = parser.parse_args()
    payload = discover_backends(args.channel)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
