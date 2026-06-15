"""
Bass Diffusion Model for technology adoption dynamics.

Used for both agentic tool adoption (by engineers) and induced demand adoption
(by new software categories entering the market).

F(t) = (1 - e^(-(p+q)*t)) / (1 + (q/p) * e^(-(p+q)*t))

Base calibration for tool adoption: p=0.03, q=0.38
Fitted approximately to GitHub Copilot adoption 2021-2024.
Confidence: LOW (single product; may not generalize to agentic tools).
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class BassParams:
    p: float = 0.03           # innovation coefficient (early adopters)
    q: float = 0.38           # imitation coefficient (word-of-mouth)
    initial_adoption: float = 0.15   # fraction using mature tools at t=0
    max_adoption: float = 0.85       # ceiling (some contexts never adopt)


def adoption_at_year(params: BassParams, year: int) -> float:
    if year == 0:
        return params.initial_adoption
    p, q = params.p, params.q
    pq = p + q
    raw_F = (1.0 - math.exp(-pq * year)) / (1.0 + (q / p) * math.exp(-pq * year))
    available = params.max_adoption - params.initial_adoption
    return min(params.max_adoption, params.initial_adoption + available * raw_F)


def adoption_trajectory(params: BassParams, n_years: int) -> List[float]:
    return [adoption_at_year(params, t) for t in range(n_years + 1)]


ADOPTION_PRESETS = {
    "slow":            BassParams(p=0.01, q=0.20, initial_adoption=0.08, max_adoption=0.70),
    "base":            BassParams(p=0.03, q=0.38, initial_adoption=0.15, max_adoption=0.85),
    "fast":            BassParams(p=0.06, q=0.55, initial_adoption=0.25, max_adoption=0.92),
    "already_adopted": BassParams(p=0.08, q=0.60, initial_adoption=0.45, max_adoption=0.95),
}
