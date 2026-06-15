"""
Dynamic demand stocks: backlog and technical debt.

V4 CORRECTIONS FROM V3 (structure unchanged):
  - Backlog: dynamic stock with inflows/outflows/equilibrium; never exhausts to zero
  - Tech debt: accumulates with AI premium; feeds back into productivity as drag

V4 BUG FIXES (this revision):
  - Backlog demand signal now returns ANNUAL FRACTION OF BASELINE OUTPUT
    consumed or released, properly scaled so 1.0 = 100% of annual output.
    A 6-month backlog at baseline = 0.5 annual output. Releasing excess over
    equilibrium in year 1 might represent 0.05-0.15 of annual output — not 0.53.
  - Debt productivity drag rescaled: 0.0003 per pct-point (not 0.003).
    40% debt now drags productivity by 1.2% not 12%.
  - Both signals are rates (fractions of annual output per year), not levels.

EMPIRICAL BASIS:
  Backlog: LOW confidence. 6-month initial backlog from proxy data (Gartner/LinearB).
  Parkinson coefficient: NO EMPIRICAL BASIS.
  Tech debt fraction: HIGH confidence (McKinsey 2023, SO 2024).
  AI debt premium: MEDIUM confidence (CMU SEI 2024: ~35% more debt from AI code).
  Debt productivity drag: LOW confidence. Rescaled from 0.003 to 0.0003 to
    reflect that debt slows engineers but doesn't eliminate productivity gains.
"""

import math
from dataclasses import dataclass


@dataclass
class BacklogParams:
    initial_months: float = 6.0
    baseline_inflow_rate: float = 1.0     # new work per year as fraction of completion rate
    parkinson_coefficient: float = 0.40   # NO EMPIRICAL BASIS
    agentic_expansion_rate: float = 0.10  # NO EMPIRICAL BASIS
    base_completion_rate: float = 2.0     # backlog turnovers per year (6mo backlog → 2×/yr)
    floor_months: float = 2.0             # structural minimum


@dataclass
class TechDebtParams:
    initial_pct: float = 40.0            # HIGH confidence: McKinsey/SO 2024
    debt_per_unit_output: float = 0.05   # LOW confidence
    ai_debt_premium: float = 0.35        # MEDIUM confidence: CMU SEI 2024
    speed_pressure_factor: float = 0.15  # NO EMPIRICAL BASIS
    base_repayment_rate: float = 0.08    # LOW confidence
    debt_focus_fraction: float = 0.20    # NO EMPIRICAL BASIS
    floor_fraction: float = 0.15         # structural minimum
    # RESCALED from 0.003 to 0.0003: debt slows engineers but doesn't dominate
    productivity_drag_per_pct: float = 0.0003  # LOW confidence


class BacklogStock:
    """
    Backlog as dynamic equilibrium stock.
    
    Demand signal is the annual engineering-output-equivalent consumed
    by excess backlog release. Scaled so that:
      - 0.10 = 10% of annual output consumed by backlog this year
      - This is the meaningful sense in which backlog creates demand
    """

    def __init__(self, params: BacklogParams):
        self.p = params
        self.B = params.initial_months
        self.B_initial = params.initial_months
        # Annual output in months (used for scaling)
        self.annual_output_months = 12.0  # 1 year = 12 months of engineering output

    def step(self, productivity_gain: float, adoption_fraction: float) -> dict:
        completion_multiplier = 1.0 + productivity_gain

        # Outflow: how much backlog gets cleared this year
        # base_completion_rate = 2.0 means without agentic tools, team clears
        # 2× their backlog per year (i.e., maintains 6mo backlog with 1× output)
        potential_outflow = self.B * self.p.base_completion_rate * completion_multiplier
        max_outflow = max(0.0, self.B - self.p.floor_months)
        outflow = min(potential_outflow, max_outflow)

        # Inflow
        baseline_inflow = self.p.baseline_inflow_rate * self.p.initial_months
        parkinson_inflow = self.p.parkinson_coefficient * productivity_gain * self.B
        agentic_inflow = self.p.agentic_expansion_rate * adoption_fraction * self.B_initial
        total_inflow = baseline_inflow + parkinson_inflow + agentic_inflow

        B_new = max(self.p.floor_months, self.B + total_inflow - outflow)

        # Equilibrium backlog level at current productivity
        B_eq = max(self.p.floor_months,
                   total_inflow / (self.p.base_completion_rate * completion_multiplier))

        # Demand signal = extra work completed this year above no-agentic baseline.
        # 
        # No-agentic equilibrium outflow = B * base_completion_rate * 1.0
        # (what would be cleared at base productivity with no agentic tools)
        # 
        # Agentic outflow = actual outflow computed above
        # 
        # Extra work done = agentic_outflow - baseline_outflow
        # Expressed as fraction of annual output (12 months)
        # Baseline equilibrium outflow = inflow at zero productivity gain
        # = what gets completed per year without agentic tools
        # This equals the baseline inflow rate times initial stock
        baseline_eq_outflow = self.p.baseline_inflow_rate * self.B_initial
        extra_work = max(0.0, outflow - baseline_eq_outflow)
        demand_signal = extra_work / self.annual_output_months

        self.B = B_new
        return {
            "demand_signal": demand_signal,
            "backlog_level": self.B,
            "backlog_equilibrium": B_eq,
            "excess_months": 0.0,
            "inflow": total_inflow,
            "outflow": outflow,
            "parkinson_inflow": parkinson_inflow,
        }


class TechDebtStock:
    """
    Technical debt as dynamic stock.
    
    Demand signal is the net engineering-output-equivalent created or consumed
    by debt dynamics this year:
      positive: refactoring work creates demand
      negative: high debt burden consumes capacity (reduces effective output)
    
    Productivity drag is the fractional reduction in engineer productivity
    from working in a high-debt codebase.
    """

    def __init__(self, params: TechDebtParams):
        self.p = params
        self.TD = params.initial_pct
        self.TD_initial = params.initial_pct
        self.TD_floor = params.initial_pct * params.floor_fraction

    def step(self, output_growth: float, adoption_fraction: float,
             debt_focus_override: float = None) -> dict:
        debt_focus = debt_focus_override if debt_focus_override is not None \
                     else self.p.debt_focus_fraction

        # Inflow: debt created by shipping
        base_debt = self.p.debt_per_unit_output * output_growth * self.TD_initial
        ai_premium = self.p.ai_debt_premium * adoption_fraction * base_debt
        speed_pressure = self.p.speed_pressure_factor * output_growth * self.TD_initial * adoption_fraction
        total_inflow = base_debt + ai_premium + speed_pressure

        # Outflow: deliberate repayment
        repayment = min(
            max(0.0, self.TD * self.p.base_repayment_rate
                + debt_focus * output_growth * self.TD_initial),
            max(0.0, self.TD - self.TD_floor)
        )

        TD_new = max(self.TD_floor, self.TD + total_inflow - repayment)

        # Near-term demand from refactoring work (POSITIVE signal).
        # Expressed as fraction of annual output.
        # Debt does NOT create negative demand — it reduces SUPPLY (captured in
        # productivity_drag). Including both would double-count the effect.
        near_term_demand = (repayment / max(1.0, self.TD_initial)) * 0.15

        net_demand = near_term_demand  # positive only

        # Productivity drag: RESCALED to 0.0003 per pct-point
        # 40% debt → 1.2% productivity drag (not 12%)
        productivity_drag = self.TD * self.p.productivity_drag_per_pct

        self.TD = TD_new
        return {
            "demand_signal": net_demand,
            "debt_level": self.TD,
            "debt_inflow": total_inflow,
            "debt_repayment": repayment,
            "ai_premium_contribution": ai_premium,
            "productivity_drag": productivity_drag,
            "near_term_demand": near_term_demand,
            "capacity_consumed": (self.TD / 100.0) * 0.30,
        }
