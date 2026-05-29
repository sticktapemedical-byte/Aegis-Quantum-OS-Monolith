from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class WilsonInterval:
    successes: int
    total: int
    p_hat: float
    confidence: float
    low: float
    high: float


def z_value(confidence: float) -> float:
    if confidence >= 0.999:
        return 3.2905267314919255
    if confidence >= 0.99:
        return 2.5758293035489004
    if confidence >= 0.95:
        return 1.959963984540054
    if confidence >= 0.90:
        return 1.6448536269514722
    return 1.959963984540054


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> WilsonInterval:
    if total < 0 or successes < 0 or successes > total:
        raise ValueError("successes and total must satisfy 0 <= successes <= total")
    if total == 0:
        return WilsonInterval(successes, total, 0.0, confidence, 0.0, 0.0)
    z = z_value(confidence)
    p_hat = successes / total
    denominator = 1.0 + (z * z / total)
    center = (p_hat + (z * z) / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt((p_hat * (1.0 - p_hat) / total) + (z * z) / (4.0 * total * total))
        / denominator
    )
    return WilsonInterval(
        successes=successes,
        total=total,
        p_hat=p_hat,
        confidence=confidence,
        low=max(0.0, center - margin),
        high=min(1.0, center + margin),
    )


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else 0.0


def sample_std(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.stdev(values) if len(values) > 1 else 0.0


def resource_cost_per_accepted_result(total_shots: int, accepted_results: int) -> float:
    if accepted_results <= 0:
        return float("inf")
    return total_shots / accepted_results
