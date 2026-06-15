"""
Firm-level backlog stock with depletion and Parkinson refill.

WHAT WAS WRONG:
  The previous firm model used backlog_months as a static demand boost:
    backlog_boost = min(0.40, self.p.backlog_months / 30.0)
  This boost was permanent — it never faded even as the backlog was worked through.
  A firm with 18 months of backlog got a 0.40 headcount boost EVERY year, forever.

WHAT THIS FIXES:
  The backlog is now a stock that depletes as engineers clear it and
  refills via a firm-specific Parkinson coefficient.

  backlog(t+1) = backlog(t) - completion(t) + parkinson_refill(t)

  completion(t) = backlog(t) × completion_rate × (1 + productivity_gain)
  parkinson_refill(t) = firm_parkinson × completion(t)

  net_clearance(t) = completion(t) - parkinson_refill(t)
                   = completion(t) × (1 - firm_parkinson)

  At equilibrium (net_clearance = 0):
    backlog_equilibrium = initial_backlog / (1 + some_factor)

  The demand factor fades from initial_backlog/initial_backlog = 1.0 (full boost)
  toward equilibrium/initial_backlog (reduced boost) as backlog depletes.

FIRM-SPECIFIC PARKINSON COEFFICIENT:
  Market-level default is 0.25. But firms differ:
  - High-growth consumer_tech startups: 0.45 (product managers demand constantly)
  - Enterprise SaaS: 0.30 (structured roadmaps, quarterly planning)
  - Regulated/government: 0.10 (procurement-limited, fixed scope)
  - Manufacturing IT: 0.15 (software is cost center, scope is controlled)

  This modulates how fast backlog refills after productivity clears it.
  Higher Parkinson → backlog persists → headcount demand stays elevated longer.
  Lower Parkinson → backlog depletes → headcount demand normalizes faster.

EMPIRICAL BASIS:
  None. These are structural assumptions consistent with the market-level
  Parkinson coefficient (0.25 base). The industry modifiers are judgment calls.
"""

from dataclasses import dataclass


# Industry-specific Parkinson coefficients
# Reflects how quickly freed engineering capacity gets filled with new scope
INDUSTRY_PARKINSON = {
    "consumer_tech":   0.45,   # product-led, high demand, continuous roadmap
    "enterprise_saas": 0.30,   # structured but competitive; quarterly planning
    "fintech":         0.20,   # regulatory constraints limit scope expansion
    "healthcare":      0.15,   # safety/compliance constraints dominate
    "manufacturing":   0.15,   # software is cost center; scope is controlled
    "government":      0.10,   # procurement-limited; scope changes are slow
    "general":         0.25,   # market average
}

# Completion rate: how much backlog gets cleared per year at baseline
# (Without agentic tools: a team turns over its backlog ~1.5× per year)
BASELINE_COMPLETION_RATE = 1.5


@dataclass
class FirmBacklogState:
    """State of firm's backlog stock at a given year."""
    backlog_months: float          # current backlog level in months
    initial_backlog_months: float  # initial level (for normalization)
    demand_factor: float           # 0.0 = no backlog boost; 1.0 = full initial boost
    completion_this_year: float    # months cleared this year
    parkinson_refill: float        # months of new scope added this year
    net_clearance: float           # net months removed this year


class FirmBacklogStock:
    """
    Simple firm-level backlog stock.

    Replaces the static backlog_boost in the original firm model.
    The demand_factor fades as backlog depletes and stabilizes at equilibrium.
    """

    def __init__(
        self,
        initial_months: float,
        industry: str = "general",
        parkinson_override: float = None,
        floor_months: float = 1.0,
    ):
        self.B = initial_months
        self.B_initial = max(0.1, initial_months)
        self.floor_months = floor_months
        self.firm_parkinson = (
            parkinson_override
            if parkinson_override is not None
            else INDUSTRY_PARKINSON.get(industry, 0.25)
        )

    def step(self, productivity_gain: float) -> FirmBacklogState:
        """
        Advance one year.
        productivity_gain: fractional gain in engineer output this year (e.g., 0.10).
        Returns FirmBacklogState with updated backlog and demand factor.
        """
        # How much backlog gets cleared this year
        completion_rate = BASELINE_COMPLETION_RATE * (1.0 + productivity_gain)
        potential_completion = self.B * completion_rate
        # Cannot clear below floor
        max_completion = max(0.0, self.B - self.floor_months)
        completion = min(potential_completion, max_completion)

        # Parkinson refill: new scope enters as capacity frees
        refill = self.firm_parkinson * completion

        # Net change
        net_clearance = completion - refill
        self.B = max(self.floor_months, self.B - net_clearance)

        # Demand factor: how much above-equilibrium backlog remains
        # At full backlog: demand_factor = 1.0 (full boost)
        # At equilibrium:  demand_factor → 0.0 (no boost above baseline)
        # Equilibrium is approximately floor_months / B_initial
        equilibrium_ratio = self.floor_months / self.B_initial
        demand_factor = max(0.0, (self.B / self.B_initial) - equilibrium_ratio)

        return FirmBacklogState(
            backlog_months=self.B,
            initial_backlog_months=self.B_initial,
            demand_factor=demand_factor,
            completion_this_year=completion,
            parkinson_refill=refill,
            net_clearance=net_clearance,
        )

    @property
    def parkinson_coefficient(self) -> float:
        return self.firm_parkinson
