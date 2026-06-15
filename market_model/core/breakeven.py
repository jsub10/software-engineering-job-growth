"""
Break-even analysis: primary output of the market model.

V5 ADDITIONS:
  - Three-component alpha: alpha_experienced, alpha_routine, alpha_cognitive
  - Cognitive scope expansion: separate from f_auto, grows more slowly
  - Cognitive leverage: senior engineers benefit more from cognitive tools

All demand and productivity values in "annual fraction of baseline engineering output."

UNIT CONSISTENCY:
  g_demand and g_productivity are both fractional annual rates.
  Employment change: ΔE(t) ≈ (g_demand - g_productivity) / phi
  Cumulative employment: E(T) = 1 + Σ_t [ margin(t) / phi × exog ]
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

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
    """
    V5: Three-component alpha replacing two-component blend.

    alpha_experienced: effect on experienced devs on mature codebases
      Source: METR RCT (Becker et al. 2025). MEDIUM confidence. Currently -0.19.
      Applies in early years when tools are immature and dev context is complex.

    alpha_routine: effect on routine/isolated tasks
      Source: BIS field experiment, Copilot studies. LOW-MEDIUM confidence. +0.20.
      Applies increasingly as tools mature (alpha shifts toward routine by year 5).

    alpha_cognitive: effect on cognitive tasks (architecture, debugging, requirements)
      Source: NO EMPIRICAL BASIS. HIGHLY SPECULATIVE.
      Represents compression of time spent on specification, decomposition,
      context synthesis, debugging hypothesis generation, requirements formalization.
      Starts near 0 (tools poor at this today), grows toward alpha_cognitive_ceiling.
      Can be set to 0.0 to reproduce v4 behavior exactly.

    f_cognitive: fraction of engineering time currently in cognitive tasks
      Source: NO EMPIRICAL BASIS. Estimated from task-time allocation studies.
      Senior: ~55-70% cognitive. Junior: ~15% cognitive. Aggregate ~35%.

    cognitive_scope_max: maximum fraction of cognitive work that becomes AI-assisted
      Source: NO EMPIRICAL BASIS. Default 0.30 (conservative).
      Represents a ceiling: some cognitive work always requires human judgment.

    cognitive_growth_rate: rate at which cognitive scope expands
      Source: NO EMPIRICAL BASIS. Default 0.15/yr.
      Slower than routine automation (harder problems take longer to crack).
    """
    # V4 components (calibrated)
    alpha_experienced: float = -0.19   # METR RCT; MEDIUM confidence
    alpha_routine: float = 0.20        # BIS/Copilot; LOW-MEDIUM confidence
    f_auto: float = 0.35               # McKinsey/SO; MEDIUM confidence
    f_verify: float = 0.25             # NO EMPIRICAL BASIS

    # V5 cognitive components (all NO EMPIRICAL BASIS)
    alpha_cognitive: float = 0.15      # productivity gain on cognitive tasks when assisted
                                        # starts near 0, grows to this value over time
    f_cognitive: float = 0.35          # fraction of engineering time in cognitive tasks
    cognitive_scope_max: float = 0.30  # max fraction of cognitive work AI can assist
    cognitive_growth_rate: float = 0.15 # rate of cognitive scope expansion per year
    cognitive_maturation_years: float = 8.0  # years for cognitive alpha to mature

    # Alpha maturation: how fast tools shift from experienced-dev drag to routine gain
    # 5 years = default (conservative); 3 years = faster tool maturation
    alpha_maturation_years: float = 5.0   # LOW confidence; structural assumption

    # Tool improvement
    g_tools: float = 0.20              # NO EMPIRICAL BASIS

    # Production function
    phi: float = 0.85                  # NO EMPIRICAL BASIS


def cognitive_scope_at_year(params: ProductivityParams, year: int) -> float:
    """
    Fraction of cognitive work that is AI-assisted at time t.
    Follows a saturating curve toward cognitive_scope_max.

    cognitive_scope(t) = cognitive_scope_max × (1 - exp(-cognitive_growth_rate × t))

    At year 0: 0% (no cognitive assistance)
    At year 5: cognitive_scope_max × (1 - e^(-0.75)) ≈ 53% of max
    (the curve keeps approaching cognitive_scope_max asymptotically for longer horizons)
    """
    return params.cognitive_scope_max * (1.0 - math.exp(-params.cognitive_growth_rate * year))


def cognitive_alpha_at_year(params: ProductivityParams, year: int) -> float:
    """
    Effective alpha for cognitive tasks at year t.
    Grows from ~0 toward alpha_cognitive as tools mature for cognitive work.
    Uses a separate (slower) maturation curve than routine alpha.
    """
    maturity = min(1.0, year / params.cognitive_maturation_years)
    return params.alpha_cognitive * maturity


def compute_productivity_growth(
    params: ProductivityParams,
    adoption_fraction: float,
    year: int,
    debt_drag: float = 0.0,
) -> float:
    """
    Annual fractional growth in output per engineer.

    V5 = V4 routine/experienced blend + V5 cognitive scope expansion term.

    Components:
      1. Tool improvement gain (compounding, modulated by adoption)
      2. Routine/experienced task gain (blended alpha, shifts from experienced → routine)
      3. Cognitive task gain (NEW V5: separate scope and alpha, slower maturation)
      4. Verification drag
      5. Debt drag

    All terms in "fraction of baseline output per engineer per year."
    """
    # 1. Tool improvement
    tool_mult = (1.0 + params.g_tools) ** year / (1.0 + params.g_tools) ** (year - 1)
    tool_gain = (tool_mult - 1.0) * adoption_fraction

    # 2. Routine/experienced task gain (V4 logic)
    maturity = min(1.0, year / params.alpha_maturation_years)
    blended_alpha = (1 - maturity) * params.alpha_experienced + maturity * params.alpha_routine
    f_auto_t = min(0.70, params.f_auto * (1.0 + 0.04 * year))
    verification_drag = params.f_verify * f_auto_t * max(0, -params.alpha_experienced)
    net_task_gain = f_auto_t * blended_alpha - verification_drag

    # 3. Cognitive task gain (V5 addition)
    cog_scope = cognitive_scope_at_year(params, year)
    cog_alpha = cognitive_alpha_at_year(params, year)
    # Cognitive gain = f_cognitive × cog_scope × cog_alpha × adoption
    # (fraction of time) × (fraction AI can assist) × (gain per assisted task) × (adoption)
    cognitive_gain = params.f_cognitive * cog_scope * cog_alpha * adoption_fraction

    # Total (before debt drag)
    g_A = tool_gain + net_task_gain * adoption_fraction + cognitive_gain - debt_drag

    return g_A


@dataclass
class BreakevenResult:
    year: int

    # Annual flow rates
    g_demand: float
    g_demand_components: Dict[str, float]
    g_productivity: float
    g_productivity_components: Dict[str, float]  # V5: decomposed productivity
    margin: float

    # Cumulative employment
    cumulative_margin: float
    employment_index: float

    # Context
    adoption_fraction: float
    backlog_level: float
    debt_level: float
    debt_productivity_drag: float

    # V5 cognitive context
    cognitive_scope: float       # fraction of cognitive work AI-assisted this year
    cognitive_gain: float        # productivity contribution from cognitive tools

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
    Run break-even analysis with v5 cognitive components.
    """
    backlog = BacklogStock(backlog_params)
    tech_debt = TechDebtStock(tech_debt_params)
    underserved = UnderservedMarketStock(underserved_params)
    induced = InducedDemandStock(induced_params)
    elasticity = ElasticityDemand(elasticity_params)

    results = []
    cumulative_margin = 0.0

    for year in range(1, n_years + 1):
        adoption = adoption_trajectory[year] if year < len(adoption_trajectory) \
                   else adoption_trajectory[-1]
        cumulative_cost_reduction = 1.0 - (1.0 - annual_cost_reduction_rate) ** year
        annual_price_reduction = (
            annual_cost_reduction_rate * (1.0 - annual_cost_reduction_rate) ** (year - 1)
        )

        # Gross productivity (for estimating output growth)
        g_A_gross = compute_productivity_growth(
            productivity_params, adoption, year, debt_drag=0.0
        )
        output_growth = max(0.0, g_A_gross)

        # Demand components
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
        g_demand = min(g_demand_raw, D_max * 0.20)
        if abs(g_demand_raw) > 0 and g_demand != g_demand_raw:
            scale = g_demand / g_demand_raw
            demand_components = {k: v * scale for k, v in demand_components.items()}

        # Net productivity (with debt drag)
        debt_drag = debt_out["productivity_drag"]
        g_A_net = compute_productivity_growth(
            productivity_params, adoption, year, debt_drag=debt_drag
        )

        # V5: decompose productivity into components for reporting
        maturity = min(1.0, year / productivity_params.alpha_maturation_years)
        blended_alpha = (1 - maturity) * productivity_params.alpha_experienced + maturity * productivity_params.alpha_routine
        f_auto_t = min(0.70, productivity_params.f_auto * (1.0 + 0.04 * year))
        tool_mult = (1.0 + productivity_params.g_tools) ** year / (1.0 + productivity_params.g_tools) ** (year - 1)
        tool_gain = (tool_mult - 1.0) * adoption
        verif_drag = productivity_params.f_verify * f_auto_t * max(0, -productivity_params.alpha_experienced)
        routine_gain = (f_auto_t * blended_alpha - verif_drag) * adoption
        cog_scope = cognitive_scope_at_year(productivity_params, year)
        cog_alpha = cognitive_alpha_at_year(productivity_params, year)
        cognitive_gain = productivity_params.f_cognitive * cog_scope * cog_alpha * adoption

        productivity_components = {
            "tool_improvement": tool_gain,
            "routine_tasks":    routine_gain,
            "cognitive_tasks":  cognitive_gain,   # V5 addition
            "debt_drag":        -debt_drag,
        }

        # Break-even
        margin = g_demand - g_A_net
        cumulative_margin += margin
        employment_index = max(0.30, 1.0 + (cumulative_margin / phi) * exog_multiplier)

        # Uncertainty
        g_demand_low = g_demand * 0.45
        g_demand_high = g_demand * 1.90
        g_prod_low = g_A_net * 0.25
        g_prod_high = g_A_net * 2.80

        results.append(BreakevenResult(
            year=year,
            g_demand=g_demand,
            g_demand_components=demand_components,
            g_productivity=g_A_net,
            g_productivity_components=productivity_components,
            margin=margin,
            cumulative_margin=cumulative_margin,
            employment_index=employment_index,
            adoption_fraction=adoption,
            backlog_level=backlog_out["backlog_level"],
            debt_level=debt_out["debt_level"],
            debt_productivity_drag=debt_drag,
            cognitive_scope=cog_scope,
            cognitive_gain=cognitive_gain,
            g_demand_low=g_demand_low,
            g_demand_high=g_demand_high,
            g_productivity_low=g_prod_low,
            g_productivity_high=g_prod_high,
        ))

    return results
