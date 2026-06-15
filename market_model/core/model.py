"""
Market model v4: primary output is break-even peak analysis, not year-by-year Jevons verdict.

PRIMARY OUTPUTS (in order of importance):
  1. break_even_year: first year employment starts declining from peak
  2. peak_employment_index: max employment above baseline
  3. employment_at_year_N: employment level at end of simulation
  4. margin_trajectory: annual (g_demand - g_productivity) — what to watch

SECONDARY OUTPUT:
  Employment index trajectory (derived from cumulative margins)
"""

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

from market_model.core.breakeven import (
    ProductivityParams, BreakevenResult, run_breakeven_analysis
)
from market_model.core.demand_stocks import BacklogParams, TechDebtParams
from market_model.core.demand_saturation import (
    UnderservedParams, InducedDemandParams, ElasticityParams
)
from market_model.core.exogenous import ExogenousParams, compute_exogenous_multiplier
from market_model.diffusion.bass import BassParams, adoption_trajectory, ADOPTION_PRESETS

SEGMENTS = ["consumer", "smb", "enterprise", "regulated"]
TIERS = ["junior", "mid", "senior", "architect"]


@dataclass
class MarketModelResult:
    scenario_name: str
    n_years: int
    breakeven: List[BreakevenResult]
    exogenous_multiplier: float
    adoption_traj: List[float]
    bass_params: BassParams

    # ── Primary outputs ──────────────────────────────────────────────────────

    @property
    def peak_employment_index(self) -> float:
        """Maximum employment index reached during simulation."""
        return max(r.employment_index for r in self.breakeven)

    @property
    def peak_year(self) -> int:
        """Year at which employment peaks."""
        return max(self.breakeven, key=lambda r: r.employment_index).year

    @property
    def break_even_year(self) -> Optional[int]:
        """
        First year employment starts declining.
        Returns None if employment never starts declining (always rising or flat).
        """
        for i in range(1, len(self.breakeven)):
            if self.breakeven[i].employment_index < self.breakeven[i-1].employment_index:
                return self.breakeven[i].year
        return None

    @property
    def final_employment_index(self) -> float:
        """Employment index at end of simulation."""
        return self.breakeven[-1].employment_index

    @property
    def pct_years_jevons_holds(self) -> float:
        return sum(1 for r in self.breakeven if r.jevons_holds) / len(self.breakeven)

    # ── Compatibility / secondary ─────────────────────────────────────────────

    @property
    def employment_index(self) -> Dict[int, float]:
        return {r.year: r.employment_index for r in self.breakeven}

    def employment_by_year(self):
        return self.employment_index

    def by_tier(self, year: int) -> Dict[str, float]:
        """
        Tier-adjusted employment at a given year.

        V5: cognitive leverage is applied on top of v4 tier adjustments.
        Senior/architect engineers benefit MORE from cognitive tools
        (they spend more time on architectural reasoning, debugging, requirements).
        Junior engineers benefit LESS (cognitive tools require expertise to direct).

        cognitive_leverage_factor (from v5_cognitive_additions.md):
          architect: 1.60 (70% cognitive work, highest leverage)
          senior:    1.40 (55% cognitive work)
          mid:       1.10 (35% cognitive work)
          junior:    0.70 (15% cognitive work, requires expertise to direct AI)

        The leverage is modulated by cognitive_scope — how much cognitive work
        is actually AI-assisted at this year. Early years: small effect.
        Later years: larger effect as cognitive scope expands.
        """
        idx = self.employment_index.get(year, 1.0)
        t = min(1.0, year / 7.0)

        # Cognitive scope at this year (from most recent breakeven result)
        cog_scope = 0.0
        if self.breakeven and year <= len(self.breakeven):
            cog_scope = self.breakeven[year - 1].cognitive_scope

        # Cognitive leverage: how much cognitive scope boosts each tier
        cog_leverage = {
            "junior":    0.70,  # LESS leverage — needs expertise to direct AI
            "mid":       1.10,
            "senior":    1.40,
            "architect": 1.60,
        }

        # Apply cognitive leverage: (leverage - 1) × cog_scope × tier_idx
        # At cog_scope=0: no cognitive effect (reverts to v4)
        # At cog_scope=0.3: cognitive leverage fully applied
        def tier_idx(base_idx, lever):
            cognitive_boost = (lever - 1.0) * cog_scope * base_idx
            return max(0.10, base_idx + cognitive_boost)

        base = {
            "junior":    max(0.10, idx * (1.0 - 0.18 * min(1.0, year / 5.0))),
            "mid":       max(0.20, idx * (1.0 - 0.04 * min(1.0, year / 5.0))),
            "senior":    max(0.30, idx * (1.0 + 0.22 * t)),
            "architect": max(0.30, idx * (1.0 + 0.28 * t)),
        }
        return {tier: tier_idx(base[tier], cog_leverage[tier]) for tier in base}

    @property
    def employment_by_tier(self) -> Dict[int, Dict[str, float]]:
        return {r.year: self.by_tier(r.year) for r in self.breakeven}

    def summary_verdict(self) -> str:
        bey = self.break_even_year
        lines = [
            f"Scenario: {self.scenario_name}",
            f"Peak employment:     {self.peak_employment_index:.3f}× baseline  (year {self.peak_year})",
            f"Break-even year:     {'never declines' if bey is None else f'year {bey} (employment starts falling)'}",
            f"Final employment:    {self.final_employment_index:.3f}× baseline  (year {self.n_years})",
            f"Exogenous mult:      {self.exogenous_multiplier:.3f}",
            f"",
            f"Year {self.n_years} demand growth:    {self.breakeven[-1].g_demand:+.2%}/yr",
            f"Year {self.n_years} productivity:     {self.breakeven[-1].g_productivity:+.2%}/yr",
            f"Year {self.n_years} margin:           {self.breakeven[-1].margin:+.2%}/yr",
            f"Flip threshold:       productivity must exceed "
            f"{self.breakeven[-1].productivity_to_flip:.2%}/yr to make employment fall",
        ]
        return "\n".join(lines)


def _build_params(config: dict):
    phi = config["production"]["phi"]

    cog = config.get("cognitive", {})
    prod = ProductivityParams(
        alpha_experienced=config["labor"]["alpha_experienced"],
        alpha_routine=config["labor"]["alpha_routine"],
        f_auto=config["labor"]["f_auto"],
        f_verify=config["labor"]["f_verify"],
        g_tools=config["labor"]["g_tools"],
        alpha_maturation_years=config["labor"].get("alpha_maturation_years", 5.0),
        phi=phi,
        # V5 cognitive additions (all NO EMPIRICAL BASIS)
        alpha_cognitive=cog.get("alpha_cognitive", 0.0),
        f_cognitive=cog.get("f_cognitive", 0.35),
        cognitive_scope_max=cog.get("cognitive_scope_max", 0.0),
        cognitive_growth_rate=cog.get("cognitive_growth_rate", 0.15),
        cognitive_maturation_years=cog.get("cognitive_maturation_years", 8.0),
    )
    elast = ElasticityParams(
        price_elasticity=config["demand"]["price_elasticity"],
        segment_weights={s: config["segments"][s]["weight"] for s in SEGMENTS},
        consumer_capture_rate=config["market"]["consumer_capture_rate"],
        market_expandability=config["demand"]["market_expandability"],
        max_cumulative_expansion=config["demand"].get("max_cumulative_expansion", 0.60),
    )
    backlog = BacklogParams(
        initial_months=config["demand"]["backlog_initial_months"],
        baseline_inflow_rate=config["demand"].get("backlog_inflow_rate", 1.0),
        parkinson_coefficient=config["demand"].get("parkinson_coefficient", 0.40),
        agentic_expansion_rate=config["demand"].get("agentic_expansion_rate", 0.10),
        base_completion_rate=config["demand"].get("backlog_completion_rate", 2.0),
        floor_months=config["demand"].get("backlog_floor_months", 2.0),
    )
    debt = TechDebtParams(
        initial_pct=config["demand"]["tech_debt_initial_pct"],
        debt_per_unit_output=config["demand"].get("debt_per_unit_output", 0.05),
        ai_debt_premium=config["demand"].get("ai_debt_premium", 0.35),
        speed_pressure_factor=config["demand"].get("speed_pressure_factor", 0.15),
        base_repayment_rate=config["demand"].get("debt_repayment_rate", 0.08),
        debt_focus_fraction=config["demand"].get("debt_focus_fraction", 0.20),
        floor_fraction=config["demand"].get("debt_floor_fraction", 0.15),
        productivity_drag_per_pct=config["demand"].get("debt_productivity_drag", 0.0003),
    )
    underserved = UnderservedParams(
        initial_fraction=config["demand"]["underserved_fraction"],
        cost_threshold=config["demand"]["underserved_threshold"],
        base_penetration_rate=config["demand"].get("underserved_penetration_rate", 0.12),
        floor_fraction=config["demand"].get("underserved_floor_fraction", 0.10),
    )
    induced = InducedDemandParams(
        total_market_size=config["demand"]["induced_market_size"],
        p_induced=config["demand"].get("induced_p", 0.02),
        q_induced=config["demand"].get("induced_q", 0.30),
        start_year=config["demand"].get("induced_start_year", 3),
    )
    bass = BassParams(
        p=config["adoption"]["p"],
        q=config["adoption"]["q"],
        initial_adoption=config["adoption"]["initial_adoption"],
        max_adoption=config["adoption"]["max_adoption"],
    )
    exog = ExogenousParams(
        gdp_environment=config["exogenous"]["gdp_environment"],
        immigration_policy=config["exogenous"]["immigration_policy"],
        education_supply=config["exogenous"]["education_supply"],
        regulatory_environment=config["exogenous"]["regulatory_environment"],
    )
    return prod, elast, backlog, debt, underserved, induced, bass, exog, phi


class MarketModel:
    def __init__(self, params: dict):
        self.params = params
        self.n_years = params["context"]["simulation_years"]

    def run(
        self,
        scenario_name: str = "base",
        exogenous_override: Optional[ExogenousParams] = None,
        bass_override: Optional[BassParams] = None,
    ) -> MarketModelResult:

        prod, elast, backlog, debt, underserved, induced, bass, exog, phi = \
            _build_params(self.params)

        if exogenous_override:
            exog = exogenous_override
        if bass_override:
            bass = bass_override

        exog_multiplier = compute_exogenous_multiplier(exog)
        adoption = adoption_trajectory(bass, self.n_years)

        breakeven = run_breakeven_analysis(
            productivity_params=prod,
            elasticity_params=elast,
            backlog_params=backlog,
            tech_debt_params=debt,
            underserved_params=underserved,
            induced_params=induced,
            adoption_trajectory=adoption,
            annual_cost_reduction_rate=self.params["context"]["annual_cost_reduction_rate"],
            n_years=self.n_years,
            D_max=self.params.get("demand", {}).get("demand_ceiling", 3.0),
            exog_multiplier=exog_multiplier,
            phi=phi,
        )

        return MarketModelResult(
            scenario_name=scenario_name,
            n_years=self.n_years,
            breakeven=breakeven,
            exogenous_multiplier=exog_multiplier,
            adoption_traj=adoption,
            bass_params=bass,
        )

    def sensitivity_analysis(self, param_path: str, values: list) -> Dict:
        results = {}
        keys = param_path.split(".")
        for v in values:
            p = copy.deepcopy(self.params)
            target = p
            for k in keys[:-1]:
                target = target[k]
            target[keys[-1]] = v
            run = MarketModel(p).run()
            be = run.breakeven[-1]
            results[v] = {
                "g_demand": be.g_demand,
                "g_productivity": be.g_productivity,
                "margin": be.margin,
                "peak_employment": run.peak_employment_index,
                "peak_year": run.peak_year,
                "break_even_year": run.break_even_year,
                "final_employment": run.final_employment_index,
                "jevons_holds": be.jevons_holds,
            }
        return results

    def monte_carlo(self, n_iterations: int = 1000, seed: int = 42) -> List[dict]:
        import random
        from market_model.core.uncertainty import UNCERTAIN_PARAMS
        random.seed(seed)
        results = []
        for _ in range(n_iterations):
            p = copy.deepcopy(self.params)
            for path, (lo, hi) in UNCERTAIN_PARAMS.items():
                keys = path.split(".")
                target = p
                for k in keys[:-1]:
                    if k not in target: break
                    target = target[k]
                else:
                    last = keys[-1]
                    if last in target and not isinstance(target.get(last), dict):
                        target[last] = random.uniform(lo, hi)
            run = MarketModel(p).run()
            results.append({
                "peak_employment": run.peak_employment_index,
                "peak_year": run.peak_year,
                "break_even_year": run.break_even_year,
                "final_employment": run.final_employment_index,
                "g_demand_yr10": run.breakeven[-1].g_demand,
                "g_productivity_yr10": run.breakeven[-1].g_productivity,
                "margin_yr10": run.breakeven[-1].margin,
            })
        return results
