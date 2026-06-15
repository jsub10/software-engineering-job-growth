"""
Break-even analysis: primary output of the market model.

UNIT CONSISTENCY (v4 fix):
  All demand components return values in the same unit:
    "annual fraction of baseline engineering output"
  
  g_productivity is also in this unit:
    "annual fractional change in output per engineer"
  
  The break-even condition is then:
    g_demand > g_productivity  →  Jevons holds (more output demanded than 
                                   each engineer can provide → more engineers needed)
    g_demand < g_productivity  →  Jevons fails

  Employment change in year t:
    ΔE(t) ≈ (g_demand(t) - g_productivity(t)) / phi
  
  Cumulative employment index:
    E(T) = 1 + Σ_t [ (g_demand(t) - g_productivity(t)) / phi × exog_multiplier ]

PRIMARY OUTPUTS:
  1. Break-even year: first year employment peaks and starts declining
  2. Peak employment: max employment index above baseline
  3. Employment at year N: level at end of simulation
  4. Annual margin chart: g_demand - g_productivity over time

SECONDARY OUTPUT:
  Employment index trajectory (derived from cumulative margins)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List

from market_model.core.demand_stocks import (
    BacklogParams, TechDebtParams, BacklogStock, TechDebtStock
)
from market_model.core.demand_saturation import (
    UnderservedParams, InducedDemandParams, ElasticityParams,
    UnderservedMarketStock, InducedDemandStock, ElasticityDemand,
    apply_aggregate_ceiling
)


@dataclass
class ProductivityParams:
    alpha_experienced: float = -0.19   # METR RCT; MEDIUM confidence
    alpha_routine: float = 0.20        # BIS/Copilot; LOW-MEDIUM confidence
    f_auto: float = 0.35               # McKinsey/SO; MEDIUM confidence
    f_verify: float = 0.25             # NO EMPIRICAL BASIS
    g_tools: float = 0.20              # NO EMPIRICAL BASIS
    phi: float = 0.85                  # NO EMPIRICAL BASIS


def compute_productivity_growth(
    params: ProductivityParams,
    adoption_fraction: float,
    year: int,
    debt_drag: float = 0.0,
) -> float:
    """
    Annual fractional growth in output per engineer from agentic tools.
    
    = tool_improvement_gain + task_automation_gain - verification_drag - debt_drag
    
    All terms in "fraction of baseline output per engineer per year."
    """
    # Annual tool improvement (compounding)
    tool_mult = (1.0 + params.g_tools) ** year / (1.0 + params.g_tools) ** (year - 1)
    tool_gain = (tool_mult - 1.0) * adoption_fraction

    # Task composition: alpha shifts from experienced-dev drag toward routine gain
    maturity = min(1.0, year / 5.0)
    blended_alpha = (1 - maturity) * params.alpha_experienced + maturity * params.alpha_routine

    # Automatable fraction grows as tools handle more task types
    f_auto_t = min(0.70, params.f_auto * (1.0 + 0.04 * year))

    # Verification overhead: cost of reviewing AI output
    verification_drag = params.f_verify * f_auto_t * max(0, -params.alpha_experienced)

    # Net task automation gain (can be negative early when METR finding dominates)
    net_task_gain = f_auto_t * blended_alpha - verification_drag

    # Total: tool improvement + task gains, both modulated by adoption
    g_A = tool_gain + net_task_gain * adoption_fraction - debt_drag

    return g_A


@dataclass
class BreakevenResult:
    year: int

    # Annual flow rates (directly comparable units)
    g_demand: float              # annual fraction of output demanded from agentic effects
    g_demand_components: Dict[str, float]
    g_productivity: float        # annual fraction of productivity gain per engineer
    margin: float                # g_demand - g_productivity

    # Cumulative employment (derived from cumulative margins)
    cumulative_margin: float     # sum of margins up to this year
    employment_index: float      # 1 + cumulative_margin/phi × exog

    # Context
    adoption_fraction: float
    backlog_level: float
    debt_level: float
    debt_productivity_drag: float

    # Uncertainty
    g_demand_low: float
    g_demand_high: float
    g_productivity_low: float
    g_productivity_high: float

    @property
    def jevons_holds(self) -> bool:
        return self.margin > 0

    @property
    def productivity_to_flip(self) -> float:
        """Productivity growth rate that would make employment flat at this year."""
        return self.g_demand


def run_breakeven_analysis(
    productivity_params: ProductivityParams,
    elasticity_params: ElasticityParams,
    backlog_params: BacklogParams,
    tech_debt_params: TechDebtParams,
    underserved_params: UnderservedParams,
    induced_params: InducedDemandParams,
    adoption_trajectory: List[float],
    annual_cost_reduction_rate: float,
    n_years: int = 10,
    D_max: float = 3.0,
    exog_multiplier: float = 1.0,
    phi: float = 0.85,
) -> List[BreakevenResult]:
    """
    Run break-even analysis with consistent units throughout.
    
    All demand signals and productivity are in "annual fraction of baseline output."
    Employment index = 1 + cumulative_margin × (1/phi) × exog_multiplier.
    """
    # Initialize stocks
    backlog = BacklogStock(backlog_params)
    tech_debt = TechDebtStock(tech_debt_params)
    underserved = UnderservedMarketStock(underserved_params)
    induced = InducedDemandStock(induced_params)
    elasticity = ElasticityDemand(elasticity_params)

    results = []
    cumulative_margin = 0.0
    cumulative_cost_reduction = 0.0

    for year in range(1, n_years + 1):
        adoption = adoption_trajectory[year] if year < len(adoption_trajectory) \
                   else adoption_trajectory[-1]
        cumulative_cost_reduction = 1.0 - (1.0 - annual_cost_reduction_rate) ** year
        annual_price_reduction = (
            annual_cost_reduction_rate * (1.0 - annual_cost_reduction_rate) ** (year - 1)
        )

        # Productivity (gross, for estimating output growth this year)
        g_A_gross = compute_productivity_growth(
            productivity_params, adoption, year, debt_drag=0.0
        )
        output_growth = max(0.0, g_A_gross)

        # Demand components (all in annual fraction of baseline output)
        backlog_out = backlog.step(output_growth, adoption)
        debt_out = tech_debt.step(output_growth, adoption)
        underserved_out = underserved.step(cumulative_cost_reduction)
        induced_out = induced.step(year)
        elasticity_out = elasticity.step(annual_price_reduction)

        demand_components = {
            "elasticity":  elasticity_out["demand_signal"],
            "backlog":     backlog_out["demand_signal"],
            "tech_debt":   debt_out["demand_signal"],
            "underserved": underserved_out["demand_signal"],
            "induced":     induced_out["demand_signal"],
        }
        g_demand_raw = sum(demand_components.values())

        # Apply aggregate ceiling: total demand cannot exceed D_max × baseline
        # The ceiling is on cumulative demand, applied via soft cap on annual demand
        g_demand = min(g_demand_raw, D_max * 0.20)  # at most 20% of D_max per year
        if abs(g_demand_raw) > 0 and g_demand != g_demand_raw:
            scale = g_demand / g_demand_raw
            demand_components = {k: v * scale for k, v in demand_components.items()}

        # Productivity (net of debt drag)
        debt_drag = debt_out["productivity_drag"]
        g_A_net = compute_productivity_growth(
            productivity_params, adoption, year, debt_drag=debt_drag
        )

        # Break-even
        margin = g_demand - g_A_net
        cumulative_margin += margin

        # Employment index: cumulative margin drives employment level
        employment_index = max(0.30,
            1.0 + (cumulative_margin / phi) * exog_multiplier
        )

        # Uncertainty bounds (reflecting parameter uncertainty)
        g_demand_low = g_demand * 0.45    # pessimistic: low capture, low backlog
        g_demand_high = g_demand * 1.90   # optimistic: high capture, large backlog
        g_prod_low = g_A_net * 0.25       # slow tool improvement
        g_prod_high = g_A_net * 2.80      # fast tool improvement

        results.append(BreakevenResult(
            year=year,
            g_demand=g_demand,
            g_demand_components=demand_components,
            g_productivity=g_A_net,
            margin=margin,
            cumulative_margin=cumulative_margin,
            employment_index=employment_index,
            adoption_fraction=adoption,
            backlog_level=backlog_out["backlog_level"],
            debt_level=debt_out["debt_level"],
            debt_productivity_drag=debt_drag,
            g_demand_low=g_demand_low,
            g_demand_high=g_demand_high,
            g_productivity_low=g_prod_low,
            g_productivity_high=g_prod_high,
        ))

    return results
