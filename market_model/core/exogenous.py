"""Exogenous multiplier: composite of macro factors outside the structural model."""
import math
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ExogenousParams:
    gdp_environment: float = 1.0
    immigration_policy: float = 1.0
    education_supply: float = 1.0
    regulatory_environment: float = 1.0
    weights: Dict[str, float] = field(default_factory=lambda: {
        "gdp_environment": 0.35,
        "immigration_policy": 0.25,
        "education_supply": 0.20,
        "regulatory_environment": 0.20,
    })
    min_value: float = 0.50
    max_value: float = 2.00


def compute_exogenous_multiplier(params: ExogenousParams) -> float:
    components = {
        "gdp_environment": params.gdp_environment,
        "immigration_policy": params.immigration_policy,
        "education_supply": params.education_supply,
        "regulatory_environment": params.regulatory_environment,
    }
    log_composite = sum(
        params.weights[k] * math.log(max(0.01, v))
        for k, v in components.items()
    )
    return max(params.min_value, min(params.max_value, math.exp(log_composite)))


EXOGENOUS_PRESETS = {
    "neutral":            ExogenousParams(1.0, 1.0, 1.0, 1.0),
    "favorable":          ExogenousParams(1.3, 1.3, 1.1, 1.1),
    "unfavorable":        ExogenousParams(0.7, 0.7, 0.9, 0.85),
    "recession":          ExogenousParams(0.6, 0.9, 0.95, 1.0),
    "ai_boom":            ExogenousParams(1.3, 1.2, 1.2, 1.1),
    "restrictive_policy": ExogenousParams(1.0, 0.6, 0.9, 0.75),
}
