"""
Firm model v4: four-way management fork with revenue saturation and absorption cap.

V4 CORRECTIONS FROM V3:
  1. Revenue saturation: logistic decay from current growth toward long-run rate,
     driven by current_market_penetration. Markets are finite.
  2. Organizational absorption cap: max 35% annual headcount growth from EXPAND.
     Engineering orgs cannot hire/onboard arbitrarily fast.
  3. IMPROVE branch: productivity gains absorbed into quality, not quantity.
     Headcount flat; debt decreases; no output quantity growth.
  4. Dynamic technical debt: each firm's debt evolves via stock-and-flow,
     with AI debt premium. Debt feeds back into effective productivity.

THE FOUR STRATEGIES:
  HARVEST:  Reduce headcount. Same output, better margin.
  REINVEST: Flat headcount. More output, grows revenue.
  EXPAND:   Grow headcount. New projects become viable at lower cost.
  IMPROVE:  Flat headcount. Same output quantity, higher quality.
            (Uses productivity gain to pay down debt and improve architecture)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from market_model.core.demand_stocks import TechDebtParams, TechDebtStock


@dataclass
class FirmProfile:
    name: str = "Unnamed Firm"
    industry: str = "general"

    # Headcount and composition
    current_headcount: int = 100
    junior_fraction: float = 0.35
    senior_fraction: float = 0.20

    # Revenue and market position
    annual_revenue_usd: float = 50_000_000
    revenue_growth_rate: float = 0.10
    long_run_growth_rate: float = 0.06       # NEW V4: where growth decays toward
    current_market_penetration: float = 0.10 # NEW V4: fraction of TAM captured

    # Software role
    software_is_core_product: bool = True
    build_buy_ratio: float = 0.80

    # Current state (firm-observable)
    backlog_months: float = 6.0
    technical_debt_pct: float = 35.0
    has_legacy_modernization: bool = False

    # Strategic posture
    will_pass_savings_to_customers: bool = False
    competitive_intensity: str = "medium"
    capital_efficiency_pressure: str = "medium"

    # Agentic adoption
    agentic_adoption_rate: float = 0.30
    adoption_maturity: str = "early"


@dataclass
class ForkWeights:
    harvest: float = 0.0
    reinvest: float = 0.0
    expand: float = 0.0
    improve: float = 0.0   # NEW V4

    @property
    def primary(self) -> str:
        m = max(self.harvest, self.reinvest, self.expand, self.improve)
        if m == self.harvest:   return "HARVEST"
        if m == self.reinvest:  return "REINVEST"
        if m == self.expand:    return "EXPAND"
        return "IMPROVE"

    def total(self) -> float:
        return self.harvest + self.reinvest + self.expand + self.improve


@dataclass
class FirmYearResult:
    year: int
    fork_weights: ForkWeights
    headcount_index: float
    headcount_absolute: int
    junior_index: float
    mid_index: float
    senior_index: float
    market_index: float
    debt_level: float
    effective_productivity_gain: float
    notes: List[str] = field(default_factory=list)


class FirmModel:
    """Firm-level headcount forecast with four-way management fork."""

    INDUSTRY_EXPAND_BIAS = {
        "consumer_tech": 1.40, "enterprise_saas": 1.10, "fintech": 0.70,
        "healthcare": 0.55, "manufacturing": 0.75, "government": 0.40, "general": 1.00,
    }
    INDUSTRY_HARVEST_BIAS = {
        "consumer_tech": 0.70, "enterprise_saas": 0.90, "fintech": 1.20,
        "healthcare": 1.30, "manufacturing": 1.25, "government": 1.40, "general": 1.00,
    }
    INDUSTRY_IMPROVE_BIAS = {
        "consumer_tech": 0.80, "enterprise_saas": 1.00, "fintech": 1.30,
        "healthcare": 1.50, "manufacturing": 1.20, "government": 1.10, "general": 1.00,
    }
    MAX_ANNUAL_HC_GROWTH = 0.35   # organizational absorption cap

    def __init__(self, profile: FirmProfile, market_result, market_params: dict):
        self.p = profile
        self.market_result = market_result
        self.market_params = market_params
        self.n_years = market_result.n_years
        self.expand_bias = self.INDUSTRY_EXPAND_BIAS.get(profile.industry, 1.0)
        self.harvest_bias = self.INDUSTRY_HARVEST_BIAS.get(profile.industry, 1.0)
        self.improve_bias = self.INDUSTRY_IMPROVE_BIAS.get(profile.industry, 1.0)

        # Initialize tech debt stock for this firm
        debt_focus = 0.40 if profile.has_legacy_modernization else 0.20
        self.debt_stock = TechDebtStock(TechDebtParams(
            initial_pct=profile.technical_debt_pct,
            ai_debt_premium=0.35,
            debt_focus_fraction=debt_focus,
            floor_fraction=0.15,
        ))

    def classify_fork(self) -> ForkWeights:
        p = self.p
        harvest_score = reinvest_score = expand_score = improve_score = 0.0

        # HARVEST
        if not p.software_is_core_product:         harvest_score += 0.35
        if not p.will_pass_savings_to_customers:
            if p.competitive_intensity == "low":   harvest_score += 0.25
            elif p.competitive_intensity == "medium": harvest_score += 0.08
        if p.capital_efficiency_pressure == "high": harvest_score += 0.20
        if p.backlog_months < 3:                   harvest_score += 0.15
        if p.competitive_intensity == "low":       harvest_score += 0.08
        harvest_score *= self.harvest_bias

        # REINVEST
        if p.software_is_core_product:             reinvest_score += 0.25
        if (not p.will_pass_savings_to_customers
                and p.competitive_intensity == "medium"): reinvest_score += 0.20
        if 3 <= p.backlog_months <= 9:             reinvest_score += 0.20
        if p.capital_efficiency_pressure == "medium": reinvest_score += 0.15
        if 20 <= p.technical_debt_pct <= 40:       reinvest_score += 0.10

        # EXPAND
        if p.will_pass_savings_to_customers:       expand_score += 0.30
        if p.competitive_intensity == "high":      expand_score += 0.25
        if p.backlog_months > 9:                   expand_score += 0.25
        if p.revenue_growth_rate > 0.20:           expand_score += 0.20
        if p.software_is_core_product and p.competitive_intensity == "high":
                                                   expand_score += 0.10
        expand_score *= self.expand_bias

        # IMPROVE (NEW V4)
        if p.technical_debt_pct > 45:              improve_score += 0.30
        if p.industry in ["healthcare", "fintech", "regulated"]: improve_score += 0.25
        if p.has_legacy_modernization:             improve_score += 0.30
        if p.current_market_penetration > 0.30:   improve_score += 0.20
        if p.technical_debt_pct > 60:              improve_score += 0.15
        improve_score *= self.improve_bias

        total = harvest_score + reinvest_score + expand_score + improve_score
        if total < 0.01:
            return ForkWeights(harvest=0.25, reinvest=0.25, expand=0.25, improve=0.25)

        return ForkWeights(
            harvest=harvest_score / total,
            reinvest=reinvest_score / total,
            expand=expand_score / total,
            improve=improve_score / total,
        )

    def _saturating_growth_rate(self, year: int) -> float:
        """
        Revenue growth that decays from current rate toward long-run rate.
        V4 CORRECTION: replaces indefinitely compounding growth.
        
        g(t) = g_long_run + (g_initial - g_long_run) × exp(-λ × t × penetration)
        
        Higher current_market_penetration → faster decay toward long-run rate.
        Low penetration → slower decay; high growth persists longer.
        """
        g_init = self.p.revenue_growth_rate
        g_lr = self.p.long_run_growth_rate
        penetration = max(0.01, self.p.current_market_penetration)
        # Saturation rate: high penetration means faster decay
        lambda_sat = penetration * 2.0
        g_t = g_lr + (g_init - g_lr) * math.exp(-lambda_sat * year)
        return max(g_lr, g_t)

    def _adoption_factor(self, year: int) -> float:
        """Adoption ramps over time from firm's current starting point."""
        maturity_map = {"early": 0.5, "developing": 0.8, "mature": 1.0}
        maturity = maturity_map.get(self.p.adoption_maturity, 0.5)
        adoption_t = min(1.0, self.p.agentic_adoption_rate + 0.07 * year) * maturity
        return adoption_t

    def _headcount_from_fork(
        self,
        fork: ForkWeights,
        market_index: float,
        year: int,
        g_productivity: float,
        adoption: float,
        prev_headcount_index: float,
    ) -> Tuple[float, Dict[str, float]]:
        """
        Derive headcount index from fork weights and market signal.

        HARVEST: headcount falls as productivity absorbed into cost savings.
        REINVEST: headcount flat; more output per engineer.
        EXPAND: headcount grows with demand; capped at absorption limit.
        IMPROVE: headcount flat; same output, higher quality.
        """
        # Accumulated productivity gain visible to this firm
        cum_cost_red = 1.0 - (1.0 - self.market_params["context"]["annual_cost_reduction_rate"]) ** year
        firm_prod_gain = g_productivity * adoption * cum_cost_red

        # HARVEST: headcount falls proportional to productivity × adoption × time
        h_harvest = max(0.35, 1.0 - firm_prod_gain * 0.6)

        # REINVEST: slightly above flat (organic growth from better output)
        h_reinvest = 1.0 + 0.025 * year

        # EXPAND: grows with demand, modulated by revenue trajectory and backlog
        g_rev = self._saturating_growth_rate(year)
        rev_factor = min(2.5, (1.0 + g_rev) ** (year * 0.30))  # partial compounding
        backlog_boost = min(0.40, self.p.backlog_months / 30.0)
        h_expand_uncapped = market_index * rev_factor * (1.0 + backlog_boost)

        # V4 CORRECTION: absorption cap — cannot grow faster than 35%/yr
        max_allowed = prev_headcount_index * (1.0 + self.MAX_ANNUAL_HC_GROWTH)
        h_expand = min(h_expand_uncapped, max_allowed)

        # IMPROVE: flat headcount, slight senior growth for quality architecture
        h_improve = 1.0 + 0.03 * min(1.0, year / 5.0)

        # Blend
        blended = (
            fork.harvest  * h_harvest  +
            fork.reinvest * h_reinvest +
            fork.expand   * h_expand   +
            fork.improve  * h_improve
        )

        contributions = {
            "harvest":  fork.harvest  * h_harvest,
            "reinvest": fork.reinvest * h_reinvest,
            "expand":   fork.expand   * h_expand,
            "improve":  fork.improve  * h_improve,
        }
        return blended, contributions

    def _tier_adjustments(self, year: int, fork: ForkWeights) -> Dict[str, float]:
        """Tier-specific adjustments by fork strategy."""
        j_frac = self.p.junior_fraction

        junior_adj = (
            fork.harvest  * max(0.20, 1.0 - j_frac * 0.70 * min(1.0, year / 4.0))
            + fork.reinvest * (1.0 - 0.08 * min(1.0, year / 5.0))
            + fork.expand   * (1.0 - 0.04 * min(1.0, year / 5.0))
            + fork.improve  * (1.0 - 0.05 * min(1.0, year / 5.0))
        )

        senior_adj = (
            fork.harvest  * (1.0 + 0.05 * min(1.0, year / 5.0))
            + fork.reinvest * (1.0 + 0.18 * min(1.0, year / 5.0))
            + fork.expand   * (1.0 + 0.30 * min(1.0, year / 5.0))
            + fork.improve  * (1.0 + 0.25 * min(1.0, year / 4.0))  # IMPROVE: senior-led
        )

        mid_adj = (
            fork.harvest  * (1.0 - 0.12 * min(1.0, year / 5.0))
            + fork.reinvest * (1.0 - 0.01 * min(1.0, year / 5.0))
            + fork.expand   * (1.0 + 0.06 * min(1.0, year / 5.0))
            + fork.improve  * (1.0 + 0.02 * min(1.0, year / 5.0))
        )

        return {
            "junior": junior_adj, "mid": mid_adj,
            "senior": senior_adj, "architect": senior_adj * 1.06
        }

    def run(self) -> List[FirmYearResult]:
        fork = self.classify_fork()
        results = []
        prev_hc_index = 1.0

        for year in range(1, self.n_years + 1):
            market_index = self.market_result.employment_index.get(year, 1.0)
            be = self.market_result.breakeven[year - 1]
            g_productivity = be.g_productivity
            adoption = self._adoption_factor(year)

            # Evolve firm's technical debt
            output_growth = max(0.0, g_productivity) * adoption
            debt_focus_override = 0.50 if fork.primary == "IMPROVE" else None
            debt_out = self.debt_stock.step(output_growth, adoption, debt_focus_override)
            effective_prod = g_productivity - debt_out["productivity_drag"]

            blended, contribs = self._headcount_from_fork(
                fork, market_index, year, effective_prod, adoption, prev_hc_index
            )
            tier_adj = self._tier_adjustments(year, fork)

            mid_frac = max(0.01, 1.0 - self.p.junior_fraction - self.p.senior_fraction)
            weighted_index = (
                self.p.junior_fraction * blended * tier_adj["junior"]
                + mid_frac            * blended * tier_adj["mid"]
                + self.p.senior_fraction * blended * tier_adj["senior"]
            )
            weighted_index = max(0.10, weighted_index)
            headcount_abs = max(1, round(self.p.current_headcount * weighted_index))

            notes = []
            lag = self.market_params.get("labor", {}).get("pipeline_lag_years", 7)
            if year >= lag:
                notes.append(f"Pipeline lag zone: potential senior shortage (lag={lag}yr).")
            if year == 2 and fork.primary == "HARVEST" and blended < 0.85:
                notes.append("HARVEST: significant headcount reduction underway by year 2.")
            if year == 3 and fork.primary == "EXPAND" and blended > 1.4:
                notes.append("EXPAND: rapid growth; absorption cap may be binding.")
            if self.p.has_legacy_modernization and year <= 3:
                notes.append("Legacy modernization: near-term engineering demand elevated.")
            if fork.primary == "IMPROVE" and year == 5:
                notes.append("IMPROVE: debt remediation completing; maintenance burden declining.")
            if debt_out["debt_level"] > self.p.technical_debt_pct * 1.3 and year == 5:
                notes.append(f"Warning: debt has grown to {debt_out['debt_level']:.0f}% "
                             f"despite agentic tools (AI debt premium effect).")

            results.append(FirmYearResult(
                year=year,
                fork_weights=fork,
                headcount_index=weighted_index,
                headcount_absolute=headcount_abs,
                junior_index=blended * tier_adj["junior"],
                mid_index=blended * tier_adj["mid"],
                senior_index=blended * tier_adj["senior"],
                market_index=market_index,
                debt_level=debt_out["debt_level"],
                effective_productivity_gain=effective_prod,
                notes=notes,
            ))
            prev_hc_index = weighted_index

        return results

    def summary(self, results: List[FirmYearResult]) -> str:
        fork = results[0].fork_weights
        final = results[-1]
        yr3 = results[2] if len(results) >= 3 else results[-1]

        lines = [
            f"\n{'='*65}",
            f"FIRM FORECAST: {self.p.name}",
            f"{'='*65}",
            f"Industry:              {self.p.industry}",
            f"Current headcount:     {self.p.current_headcount}",
            f"Software core product: {self.p.software_is_core_product}",
            f"Build/buy:             {self.p.build_buy_ratio:.0%}",
            f"Market penetration:    {self.p.current_market_penetration:.0%} of TAM",
            f"Initial growth rate:   {self.p.revenue_growth_rate:.0%}/yr → "
            f"{self.p.long_run_growth_rate:.0%}/yr long-run",
            f"",
            f"MANAGEMENT FORK:",
            f"  Primary: {fork.primary}",
            f"  HARVEST  {fork.harvest:.0%} | REINVEST {fork.reinvest:.0%} | "
            f"EXPAND {fork.expand:.0%} | IMPROVE {fork.improve:.0%}",
            f"",
        ]

        if fork.primary == "HARVEST":
            lines.append("  → Efficiency gains captured as margin reduction. Headcount falls.")
        elif fork.primary == "REINVEST":
            lines.append("  → Efficiency gains reinvested in more output. Headcount roughly flat.")
        elif fork.primary == "EXPAND":
            lines.append("  → New projects now viable. Headcount grows (absorption-capped at 35%/yr).")
        else:
            lines.append("  → Efficiency gains used for quality/debt. Headcount roughly flat.")

        lines += [
            f"",
            f"YEAR 3:  HC index {yr3.headcount_index:.3f} → {yr3.headcount_absolute} engineers  "
            f"(vs market {yr3.market_index:.3f})  debt {yr3.debt_level:.0f}%",
            f"YEAR {self.n_years}: HC index {final.headcount_index:.3f} → {final.headcount_absolute} engineers  "
            f"(vs market {final.market_index:.3f})  debt {final.debt_level:.0f}%",
            f"",
            f"  Junior yr{self.n_years}: {final.junior_index:.3f}  "
            f"Mid: {final.mid_index:.3f}  "
            f"Senior: {final.senior_index:.3f}",
            f"",
            f"NOTES:",
        ]

        seen = set()
        for r in results:
            for note in r.notes:
                if note not in seen:
                    lines.append(f"  yr{r.year}: {note}")
                    seen.add(note)
        if not seen:
            lines.append("  No major flags.")

        return "\n".join(lines)
