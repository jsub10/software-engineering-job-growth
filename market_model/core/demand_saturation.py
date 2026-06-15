"""
Saturating demand components: underserved markets and induced demand.

KEY CORRECTIONS FROM V3:
  v3 let both of these grow indefinitely. v4 models them with explicit
  depletion and saturation mechanisms.

UNDERSERVED MARKETS:
  A finite stock that depletes as markets get penetrated.
  U(t+1) = U(t) - penetration(t)
  Demand signal = annual penetration flow (not cumulative stock)

INDUCED DEMAND:
  New software categories that don't yet exist, modeled as a new market
  that itself follows Bass diffusion. The total size is bounded.
  Annual demand = derivative of Bass curve × total induced market size

AGGREGATE CEILING:
  After all demand components are summed, a logistic saturation caps
  the total demand ratio at a maximum value (default 3.0×).
  This prevents the physically impossible case of software consuming
  an unbounded fraction of economic activity.
"""

import math
from dataclasses import dataclass
from typing import List


@dataclass
class UnderservedParams:
    """Parameters for underserved market stock."""

    # Initial underserved market size as fraction of current software market
    initial_fraction: float = 0.25      # NO EMPIRICAL BASIS: pure assumption

    # Cost threshold to unlock (fraction of cost that must fall)
    cost_threshold: float = 0.40        # NO EMPIRICAL BASIS

    # Annual penetration rate once unlocked
    base_penetration_rate: float = 0.12 # 12%/yr of remaining underserved market
                                          # LOW confidence: loosely analogous to SMB SaaS adoption

    # Floor: some markets remain permanently underserved
    floor_fraction: float = 0.10        # 10% of initial underserved market never gets served
                                          # (geographic, regulatory, willingness-to-pay barriers)


@dataclass
class InducedDemandParams:
    """Parameters for induced demand (new software categories)."""

    # Total size of new market categories created by agentic coding
    # as fraction of current software market
    total_market_size: float = 0.20     # NO EMPIRICAL BASIS: new categories = 20% of current market
                                          # This is speculative; wide uncertainty range

    # Bass diffusion parameters for new category adoption
    # Separate from tool adoption: these govern how fast new categories mature
    p_induced: float = 0.02             # innovation: new categories emerge slowly
    q_induced: float = 0.30             # imitation: once one new category succeeds, others follow

    # Lag: new categories don't start emerging until tools have been around a few years
    start_year: int = 3


@dataclass
class ElasticityParams:
    """Parameters for price-elasticity-driven demand expansion."""

    # Elasticity by segment
    price_elasticity: dict = None

    # Segment weights
    segment_weights: dict = None

    # Consumer capture rate by segment
    consumer_capture_rate: dict = None

    # Market expandability ceiling by segment
    market_expandability: dict = None

    # Maximum cumulative demand expansion from elasticity
    # (Baumol constraint: complements become binding)
    max_cumulative_expansion: float = 0.60  # elasticity can add at most 60% above baseline
                                              # NO EMPIRICAL BASIS; reflects Baumol constraint

    def __post_init__(self):
        if self.price_elasticity is None:
            self.price_elasticity = {
                "consumer": 1.80, "smb": 1.40,
                "enterprise": 0.45, "regulated": 0.20
            }
        if self.segment_weights is None:
            self.segment_weights = {
                "consumer": 0.20, "smb": 0.25,
                "enterprise": 0.40, "regulated": 0.15
            }
        if self.consumer_capture_rate is None:
            self.consumer_capture_rate = {
                "consumer": 0.70, "smb": 0.55,
                "enterprise": 0.30, "regulated": 0.20
            }
        if self.market_expandability is None:
            self.market_expandability = {
                "consumer": 0.60, "smb": 0.80,
                "enterprise": 0.30, "regulated": 0.20
            }


class UnderservedMarketStock:
    """
    Underserved market as a depleting stock.
    Once unlocked by sufficient cost reduction, the market gets penetrated
    at a rate proportional to remaining stock. Exhausts as it is served.
    """

    def __init__(self, params: UnderservedParams):
        self.p = params
        self.U = params.initial_fraction              # remaining underserved market
        self.U_initial = params.initial_fraction
        self.U_floor = params.initial_fraction * params.floor_fraction
        self.cumulative_penetrated = 0.0

    def step(self, cumulative_cost_reduction: float) -> dict:
        """Advance one year. Returns demand signal (flow of newly penetrated market)."""

        # Not yet unlocked
        if cumulative_cost_reduction < self.p.cost_threshold:
            return {
                "demand_signal": 0.0,
                "remaining_stock": self.U,
                "penetration_this_year": 0.0,
                "unlocked": False,
            }

        # Activation ramp: demand grows as cost reduction exceeds threshold
        activation = min(1.0,
            (cumulative_cost_reduction - self.p.cost_threshold) / self.p.cost_threshold
        )

        # Annual penetration flow
        available = max(0.0, self.U - self.U_floor)
        penetration = available * self.p.base_penetration_rate * activation

        # Demand signal is the penetration flow (not cumulative stock)
        demand_signal = penetration / max(0.001, self.U_initial)

        # Deplete stock
        self.U = max(self.U_floor, self.U - penetration)
        self.cumulative_penetrated += penetration

        return {
            "demand_signal": demand_signal,
            "remaining_stock": self.U,
            "penetration_this_year": penetration,
            "unlocked": True,
            "pct_exhausted": self.cumulative_penetrated / max(0.001, self.U_initial),
        }


class InducedDemandStock:
    """
    Induced demand: new software categories that emerge as agentic tools mature.
    Modeled as a finite new market following Bass diffusion.
    Annual demand = growth rate of new category adoption × total market size.
    """

    def __init__(self, params: InducedDemandParams):
        self.p = params
        self.prev_F = 0.0

    def step(self, year: int) -> dict:
        """Advance one year. Returns demand signal."""

        if year < self.p.start_year:
            return {"demand_signal": 0.0, "cumulative_penetration": 0.0}

        t = year - self.p.start_year + 1  # time since categories started emerging
        p, q = self.p.p_induced, self.p.q_induced
        pq = p + q

        # Bass F(t) for new category adoption
        F = (1.0 - math.exp(-pq * t)) / (1.0 + (q / p) * math.exp(-pq * t))
        F = min(1.0, F)

        # Annual demand = growth in penetration × total market size
        dF = F - self.prev_F
        demand_signal = dF * self.p.total_market_size
        self.prev_F = F

        return {
            "demand_signal": demand_signal,
            "cumulative_penetration": F,
            "total_induced_demand_captured": F * self.p.total_market_size,
        }


class ElasticityDemand:
    """
    Price-elasticity-driven demand expansion.
    Applies a cumulative cap reflecting the Baumol constraint:
    as software gets cheaper, other inputs (PM, design, sales) become binding.
    """

    def __init__(self, params: ElasticityParams):
        self.p = params
        self.cumulative_expansion = 0.0

    def weighted_elasticity(self) -> float:
        total = 0.0
        for seg, weight in self.p.segment_weights.items():
            eff = (self.p.price_elasticity[seg]
                   * self.p.consumer_capture_rate[seg]
                   * self.p.market_expandability[seg])
            total += weight * eff
        return total

    def step(self, annual_price_reduction: float) -> dict:
        """Advance one year. Returns demand signal."""
        eff_elasticity = self.weighted_elasticity()
        annual_expansion = eff_elasticity * annual_price_reduction

        # Apply cumulative cap
        remaining_capacity = max(0.0,
            self.p.max_cumulative_expansion - self.cumulative_expansion
        )
        actual_expansion = min(annual_expansion, remaining_capacity)
        self.cumulative_expansion += actual_expansion

        return {
            "demand_signal": actual_expansion,
            "cumulative_expansion": self.cumulative_expansion,
            "cap_remaining": remaining_capacity - actual_expansion,
            "weighted_elasticity": eff_elasticity,
        }


def apply_aggregate_ceiling(D_raw: float, D_max: float = 3.0, steepness: float = 4.0) -> float:
    """
    Apply soft ceiling to total demand ratio using a smooth clamp.
    Prevents physically impossible unlimited growth as costs approach zero.

    D_max: maximum plausible demand ratio (default 3.0 = software market triples)
    steepness: how sharply the ceiling kicks in (higher = sharper)

    Behavior:
      D_raw << D_max:   D_saturated ≈ D_raw   (ceiling not binding)
      D_raw → D_max:    D_saturated → D_max    (ceiling softly binds)
      D_raw >> D_max:   D_saturated stays near D_max  (hard ceiling)
    
    Uses a smooth function: D_sat = D_max × tanh(D_raw / D_max)
    which maps [0, ∞) → [0, D_max) smoothly and is well-behaved.
    For D_raw << D_max: tanh(x) ≈ x, so D_sat ≈ D_raw (pass-through)
    For D_raw → ∞: tanh → 1, so D_sat → D_max (ceiling binds)
    """
    if D_raw <= 1.0:
        return max(0.5, D_raw)
    # Smooth ceiling: passes through at low values, asymptotes at D_max
    D_saturated = D_max * math.tanh(D_raw / D_max)
    return max(1.0, min(D_max, D_saturated))
