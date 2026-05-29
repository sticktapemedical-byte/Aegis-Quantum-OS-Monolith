from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

from aegis_stats import mean


@dataclass(frozen=True)
class EfficiencySummary:
    total_shots: int
    total_jobs: int
    accepted_results: int
    rerun_count: int
    shots_per_accepted_result: float
    jobs_per_accepted_result: float
    rerun_rate: float
    mean_accepted_quality: float


def is_accepted(record: dict, q_conf_threshold: float = 0.90, ghz_threshold: float = 0.90) -> bool:
    explicit_gates = [
        record[key]
        for key in ("continuity_gate_passed", "aegis_raw_continuity_gate_passed")
        if key in record
    ]
    if explicit_gates and not any(bool(value) for value in explicit_gates):
        return False
    if "q_conf" in record and float(record["q_conf"]) < q_conf_threshold:
        return False
    if "aegis_raw_q_conf" in record and float(record["aegis_raw_q_conf"]) < q_conf_threshold:
        return False
    if "ghz_population" in record:
        return float(record["ghz_population"]) >= ghz_threshold
    if "raw_ghz_population" in record:
        return float(record["raw_ghz_population"]) >= ghz_threshold
    if "setpoint_validations_passed" in record:
        return int(record.get("setpoint_validations_passed", 0)) > 0
    return bool(record.get("qom_compact_payload_hex")) and bool(record.get("merkle_root"))


def record_shots(record: dict) -> int:
    for key in ("total_shots", "shots", "ghz_shots"):
        value = record.get(key)
        if isinstance(value, int):
            return value
    return 0


def quality_value(record: dict) -> float:
    for key in ("ghz_population", "raw_ghz_population", "mitigated_ghz_population", "q_conf", "aegis_raw_q_conf"):
        if key in record:
            return float(record[key])
    return 0.0


def summarize_efficiency(records: Iterable[dict], q_conf_threshold: float = 0.90, ghz_threshold: float = 0.90) -> EfficiencySummary:
    rows = list(records)
    accepted = [row for row in rows if is_accepted(row, q_conf_threshold=q_conf_threshold, ghz_threshold=ghz_threshold)]
    rejected = [row for row in rows if row not in accepted]
    total_shots = sum(record_shots(row) for row in rows)
    total_jobs = len(rows)
    accepted_count = len(accepted)
    shots_per = total_shots / accepted_count if accepted_count else float("inf")
    jobs_per = total_jobs / accepted_count if accepted_count else float("inf")
    rerun_rate = len(rejected) / total_jobs if total_jobs else 0.0
    return EfficiencySummary(
        total_shots=total_shots,
        total_jobs=total_jobs,
        accepted_results=accepted_count,
        rerun_count=len(rejected),
        shots_per_accepted_result=shots_per,
        jobs_per_accepted_result=jobs_per,
        rerun_rate=rerun_rate,
        mean_accepted_quality=mean(quality_value(row) for row in accepted),
    )


def finite_or_none(value: float) -> float | None:
    return value if isfinite(value) else None


def summary_to_dict(summary: EfficiencySummary) -> dict[str, object]:
    return {
        "total_shots": summary.total_shots,
        "total_jobs": summary.total_jobs,
        "accepted_results": summary.accepted_results,
        "rerun_count": summary.rerun_count,
        "shots_per_accepted_result": finite_or_none(summary.shots_per_accepted_result),
        "jobs_per_accepted_result": finite_or_none(summary.jobs_per_accepted_result),
        "rerun_rate": summary.rerun_rate,
        "mean_accepted_quality": summary.mean_accepted_quality,
    }
