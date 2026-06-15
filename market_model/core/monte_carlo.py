"""
Comprehensive Monte Carlo simulation for market and firm models.

Draws parameters from distributions defined in variable_documentation.md.
Reports results for both models with full statistical summaries.

Usage:
    python run.py --monte-carlo [--iterations N] [--firm PROFILE] [--mc-output all]

KEY DESIGN DECISIONS:
  - Parameters drawn from UNIFORM distributions within [mc_low, mc_high].
    Uniform is used because we have no basis for assigning probabilities
    within the plausible range; it correctly represents ignorance.
  - Parameters with NO EMPIRICAL BASIS get WIDER ranges (appropriate humility).
  - Parameters with HIGH confidence get NARROWER ranges.
  - Some parameters are drawn jointly to avoid physically impossible combinations
    (e.g., junior_fraction + senior_fraction must be < 1.0).
  - Boolean/categorical firm parameters are drawn from a representative distribution
    reflecting real-world firm population.

INTERPRETATION:
  Monte Carlo output is NOT a probability distribution over futures.
  It is a distribution over model outputs given parameter uncertainty.
  The 10th-90th percentile range tells you: if you believe parameters
  lie within these ranges, outcomes lie within this employment range.
  It does NOT say the 50th percentile is "most likely."
"""

import copy
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import yaml


# ─────────────────────────────────────────────────────────────────────────────
# PARAMETER RANGES
# All ranges are [mc_low, mc_high] from variable_documentation.md
# ─────────────────────────────────────────────────────────────────────────────

MARKET_MC_PARAMS = {
    # NONE confidence — widest ranges
    "labor.g_tools":                     (0.08, 0.45),
    "demand.parkinson_coefficient":       (0.05, 0.50),
    "context.annual_cost_reduction_rate": (0.04, 0.25),
    "labor.f_verify":                     (0.08, 0.50),
    "demand.underserved_fraction":        (0.00, 0.55),
    "demand.underserved_threshold":       (0.15, 0.65),
    "demand.induced_market_size":         (0.00, 0.45),
    "demand.max_cumulative_expansion":    (0.20, 1.00),
    "production.phi":                     (0.70, 0.97),
    "demand.agentic_expansion_rate":      (0.02, 0.25),
    # Cognitive — all NONE confidence
    "cognitive.alpha_cognitive":          (0.00, 0.30),
    "cognitive.cognitive_scope_max":      (0.00, 0.55),
    "cognitive.cognitive_growth_rate":    (0.05, 0.35),
    "cognitive.cognitive_maturation_years": (4.0, 14.0),
    # LOW confidence
    "labor.alpha_maturation_years":       (2.0, 8.0),
    "adoption.q":                         (0.20, 0.55),
    "adoption.initial_adoption":          (0.08, 0.35),
    "adoption.max_adoption":              (0.70, 0.95),
    "demand.backlog_initial_months":      (3.0, 12.0),
    # MEDIUM confidence — tighter
    "labor.alpha_experienced":            (-0.40, 0.05),
    "labor.alpha_routine":                (0.05, 0.45),
    "labor.f_auto":                       (0.20, 0.55),
    "demand.tech_debt_initial_pct":       (25.0, 58.0),
    "demand.ai_debt_premium":             (0.10, 0.65),
    # LOW-MEDIUM capture rates
    "market.consumer_capture_rate.consumer":   (0.35, 0.90),
    "market.consumer_capture_rate.smb":        (0.25, 0.80),
    "market.consumer_capture_rate.enterprise": (0.10, 0.60),
    "market.consumer_capture_rate.regulated":  (0.05, 0.45),
}

FIRM_MC_PARAMS = {
    # Continuous firm profile parameters
    "junior_fraction":           (0.20, 0.55),
    "senior_fraction":           (0.12, 0.35),
    "revenue_growth_rate":       (0.02, 0.35),
    "long_run_growth_rate":      (0.03, 0.10),
    "current_market_penetration":(0.02, 0.50),
    "build_buy_ratio":           (0.30, 0.98),
    "backlog_months":            (2.0, 18.0),
    "technical_debt_pct":        (15.0, 60.0),
    "agentic_adoption_rate":     (0.05, 0.70),
}

# Categorical firm parameters — drawn from discrete distributions
FIRM_CATEGORICAL = {
    "industry": {
        "consumer_tech": 0.15,
        "enterprise_saas": 0.25,
        "fintech": 0.15,
        "healthcare": 0.10,
        "manufacturing": 0.15,
        "government": 0.10,
        "general": 0.10,
    },
    "competitive_intensity": {"low": 0.30, "medium": 0.45, "high": 0.25},
    "capital_efficiency_pressure": {"low": 0.25, "medium": 0.50, "high": 0.25},
    "adoption_maturity": {"early": 0.45, "developing": 0.40, "mature": 0.15},
    "will_pass_savings_to_customers": {True: 0.35, False: 0.65},
    "software_is_core_product": {True: 0.55, False: 0.45},
    "has_legacy_modernization": {True: 0.20, False: 0.80},
}


def _draw_categorical(dist: dict, rng: random.Random) -> object:
    """Draw from a categorical distribution defined as {value: probability}."""
    r = rng.random()
    cumulative = 0.0
    for value, prob in dist.items():
        cumulative += prob
        if r <= cumulative:
            return value
    return list(dist.keys())[-1]


def _set_nested(d: dict, path: str, value) -> None:
    """Set a value at a dot-separated path in a nested dict."""
    keys = path.split(".")
    target = d
    for k in keys[:-1]:
        target = target[k]
    target[keys[-1]] = value


def _get_nested(d: dict, path: str):
    """Get a value at a dot-separated path."""
    keys = path.split(".")
    target = d
    for k in keys:
        target = target[k]
    return target


@dataclass
class MarketMCResult:
    """Result of a single Monte Carlo draw for the market model."""
    peak_employment: float
    peak_year: int
    break_even_year: Optional[int]
    final_employment: float
    g_demand_yr10: float
    g_productivity_yr10: float
    margin_yr10: float
    params_drawn: dict = field(default_factory=dict)


@dataclass
class FirmMCResult:
    """Result of a single Monte Carlo draw for the firm model."""
    peak_employment: float
    peak_year: int
    break_even_year: Optional[int]
    final_employment: float
    final_junior: float
    final_senior: float
    fork_primary: str
    firm_profile_summary: dict = field(default_factory=dict)
    market_final: float = 1.0


def run_market_monte_carlo(
    base_params: dict,
    n_iterations: int = 1000,
    seed: int = 42,
) -> List[MarketMCResult]:
    """
    Run Monte Carlo simulation over market model parameter uncertainty.
    Each iteration draws all MARKET_MC_PARAMS and runs the full model.
    """
    from market_model.core.model import MarketModel

    rng = random.Random(seed)
    results = []

    for i in range(n_iterations):
        p = copy.deepcopy(base_params)

        # Draw continuous parameters
        drawn = {}
        for path, (lo, hi) in MARKET_MC_PARAMS.items():
            # Handle nested capture_rate specially
            if "consumer_capture_rate." in path:
                segment = path.split(".")[-1]
                v = rng.uniform(lo, hi)
                p["market"]["consumer_capture_rate"][segment] = v
                drawn[path] = v
            else:
                v = rng.uniform(lo, hi)
                _set_nested(p, path, v)
                drawn[path] = v

        # Enforce constraint: junior_fraction + senior_fraction < 0.95
        # (not a market model parameter, but keep for firm MC consistency)

        try:
            run = MarketModel(p).run(scenario_name=f"mc_{i}")
            results.append(MarketMCResult(
                peak_employment=run.peak_employment_index,
                peak_year=run.peak_year,
                break_even_year=run.break_even_year,
                final_employment=run.final_employment_index,
                g_demand_yr10=run.breakeven[-1].g_demand,
                g_productivity_yr10=run.breakeven[-1].g_productivity,
                margin_yr10=run.breakeven[-1].margin,
                params_drawn=drawn,
            ))
        except Exception:
            # Skip failed runs (rare, e.g., numerical edge cases)
            pass

    return results


def run_firm_monte_carlo(
    base_market_params: dict,
    base_firm_profile: dict,
    n_iterations: int = 500,
    seed: int = 42,
    vary_firm_params: bool = True,
    vary_market_params: bool = True,
) -> List[FirmMCResult]:
    """
    Run Monte Carlo for the firm model.
    Varies both firm profile parameters and market model parameters.
    This gives the full distribution of firm outcomes given uncertainty
    in both what the firm looks like and what the market does.
    """
    from market_model.core.model import MarketModel
    from firm_model.core.firm_model import FirmModel, FirmProfile

    rng = random.Random(seed)
    results = []

    for i in range(n_iterations):
        # Draw market parameters
        mp = copy.deepcopy(base_market_params)
        if vary_market_params:
            for path, (lo, hi) in MARKET_MC_PARAMS.items():
                if "consumer_capture_rate." in path:
                    segment = path.split(".")[-1]
                    mp["market"]["consumer_capture_rate"][segment] = rng.uniform(lo, hi)
                else:
                    _set_nested(mp, path, rng.uniform(lo, hi))

        # Draw firm profile parameters
        fp = copy.deepcopy(base_firm_profile)
        if vary_firm_params:
            for field_name, (lo, hi) in FIRM_MC_PARAMS.items():
                # Vary around the base profile value if it exists and is reasonable
                # This keeps the firm type anchored while exploring uncertainty
                base_val = base_firm_profile.get(field_name)
                if base_val is not None and isinstance(base_val, (int, float)):
                    # Vary within ±50% of base value, clipped to hard range
                    spread = (hi - lo) * 0.5
                    lo_adj = max(lo, base_val - spread)
                    hi_adj = min(hi, base_val + spread)
                    fp[field_name] = rng.uniform(lo_adj, hi_adj)
                else:
                    fp[field_name] = rng.uniform(lo, hi)
            # Only draw categoricals if profile is generic; else use profile values
            is_generic = base_firm_profile.get("name", "").startswith("Generic")
            for field_name, dist in FIRM_CATEGORICAL.items():
                if is_generic:
                    fp[field_name] = _draw_categorical(dist, rng)
                # else: keep base profile's categorical values

            # Enforce: junior + senior < 0.90 (leave room for mid)
            if fp["junior_fraction"] + fp["senior_fraction"] > 0.90:
                total = fp["junior_fraction"] + fp["senior_fraction"]
                fp["junior_fraction"] = fp["junior_fraction"] / total * 0.88
                fp["senior_fraction"] = fp["senior_fraction"] / total * 0.88

        try:
            market_run = MarketModel(mp).run(scenario_name=f"firm_mc_{i}")
            profile = FirmProfile(**{k: v for k, v in fp.items()
                                     if k in FirmProfile.__dataclass_fields__})
            firm = FirmModel(profile, market_run, mp)
            firm_results = firm.run()

            final = firm_results[-1]
            indices = [r.headcount_index for r in firm_results]
            peak_idx = max(range(len(indices)), key=lambda i: indices[i])

            # Find firm break-even year
            firm_bey = None
            for j in range(1, len(firm_results)):
                if firm_results[j].headcount_index < firm_results[j-1].headcount_index:
                    firm_bey = firm_results[j].year
                    break

            results.append(FirmMCResult(
                peak_employment=max(indices),
                peak_year=firm_results[peak_idx].year,
                break_even_year=firm_bey,
                final_employment=final.headcount_index,
                final_junior=final.junior_index,
                final_senior=final.senior_index,
                fork_primary=final.fork_weights.primary,
                firm_profile_summary={
                    "industry": fp.get("industry", "general"),
                    "software_is_core": fp.get("software_is_core_product", True),
                    "competitive": fp.get("competitive_intensity", "medium"),
                    "junior_frac": fp.get("junior_fraction", 0.35),
                    "backlog_months": fp.get("backlog_months", 6.0),
                    "tech_debt_pct": fp.get("technical_debt_pct", 35.0),
                },
                market_final=market_run.final_employment_index,
            ))
        except Exception:
            pass

    return results


# ─────────────────────────────────────────────────────────────────────────────
# REPORTING
# ─────────────────────────────────────────────────────────────────────────────

def _pct(values: list, p: float) -> float:
    """Return p-th percentile of values list."""
    s = sorted(values)
    idx = max(0, min(len(s)-1, int(p / 100 * len(s))))
    return s[idx]


def print_market_mc_report(results: List[MarketMCResult]) -> None:
    n = len(results)
    if n == 0:
        print("No results to report.")
        return

    peaks = [r.peak_employment for r in results]
    peak_yrs = [r.peak_year for r in results]
    beys = [r.break_even_year for r in results if r.break_even_year is not None]
    bey_nevers = sum(1 for r in results if r.break_even_year is None)
    finals = [r.final_employment for r in results]
    margins = [r.margin_yr10 * 100 for r in results]  # in percent
    g_demands = [r.g_demand_yr10 * 100 for r in results]
    g_prods = [r.g_productivity_yr10 * 100 for r in results]

    pct_above_1 = sum(1 for r in results if r.final_employment > 1.0) / n
    pct_jevons_yr10 = sum(1 for r in results if r.margin_yr10 > 0) / n

    print(f"\n{'='*70}")
    print(f"MARKET MODEL MONTE CARLO RESULTS  (n={n} iterations)")
    print(f"{'='*70}")
    print(f"\nNOTE: These are distributions over model outputs given parameter")
    print(f"uncertainty. They are NOT probability forecasts of future employment.")
    print(f"Wide ranges reflect parameter ignorance, not stochastic futures.")

    print(f"\n── PRIMARY OUTPUTS ──────────────────────────────────────────────")
    print(f"  {'':30}  {'P10':>8}  {'P25':>8}  {'P50':>8}  {'P75':>8}  {'P90':>8}")
    print(f"  {'':30}  {'----':>8}  {'----':>8}  {'----':>8}  {'----':>8}  {'----':>8}")

    def row(label, vals, fmt=".3f"):
        print(f"  {label:<30}  {_pct(vals,10):>8{fmt}}  {_pct(vals,25):>8{fmt}}  "
              f"{_pct(vals,50):>8{fmt}}  {_pct(vals,75):>8{fmt}}  {_pct(vals,90):>8{fmt}}")

    row("Peak employment index", peaks)
    row("Peak year", peak_yrs, ".0f")
    if beys:
        row("Break-even year (when declined)", beys, ".0f")
    print(f"  {'Employment never declines':30}  {bey_nevers/n:>7.1%} of runs")
    row("Final employment (yr 10)", finals)

    print(f"\n── BREAK-EVEN MARGIN (year 10) ──────────────────────────────────")
    row("Demand growth %/yr", g_demands, ".1f")
    row("Productivity growth %/yr", g_prods, ".1f")
    row("Margin (D - P) %/yr", margins, ".1f")
    print(f"  {'Jevons holds at yr 10':30}  {pct_jevons_yr10:>8.1%} of runs")

    print(f"\n── VERDICTS ─────────────────────────────────────────────────────")
    print(f"  Final employment > baseline (1.0):  {pct_above_1:.1%} of runs")
    print(f"  Final employment > 1.1×:            {sum(1 for r in results if r.final_employment > 1.1)/n:.1%} of runs")
    print(f"  Final employment < 0.9×:            {sum(1 for r in results if r.final_employment < 0.9)/n:.1%} of runs")
    print(f"  Final employment < 0.7×:            {sum(1 for r in results if r.final_employment < 0.7)/n:.1%} of runs")

    # Dominant parameter influence
    print(f"\n── PARAMETER INFLUENCE ──────────────────────────────────────────")
    print(f"  Pearson correlation between drawn parameters and final employment:")

    # Compute correlations for top parameters
    param_names = list(results[0].params_drawn.keys()) if results[0].params_drawn else []
    correlations = []
    for param in param_names:
        vals = [r.params_drawn.get(param, 0) for r in results]
        outcomes = finals
        n_vals = len(vals)
        if n_vals < 2:
            continue
        mean_v = sum(vals) / n_vals
        mean_o = sum(outcomes) / n_vals
        cov = sum((vals[i] - mean_v) * (outcomes[i] - mean_o) for i in range(n_vals))
        std_v = math.sqrt(sum((v - mean_v)**2 for v in vals))
        std_o = math.sqrt(sum((o - mean_o)**2 for o in outcomes))
        if std_v > 0 and std_o > 0:
            corr = cov / (std_v * std_o)
            correlations.append((param, corr))

    correlations.sort(key=lambda x: abs(x[1]), reverse=True)
    for param, corr in correlations[:8]:
        direction = "↑ emp rises" if corr > 0 else "↑ emp falls"
        print(f"  {param:<42}  r={corr:>+.3f}  ({direction} with higher values)")

    print(f"\n{'='*70}")


def print_firm_mc_report(results: List[FirmMCResult], profile_name: str = "") -> None:
    n = len(results)
    if n == 0:
        print("No firm MC results to report.")
        return

    peaks = [r.peak_employment for r in results]
    finals = [r.final_employment for r in results]
    juniors = [r.final_junior for r in results]
    seniors = [r.final_senior for r in results]
    beys = [r.break_even_year for r in results if r.break_even_year is not None]
    bey_nevers = sum(1 for r in results if r.break_even_year is None)
    market_finals = [r.market_final for r in results]

    # Fork distribution
    fork_counts = {}
    for r in results:
        fork_counts[r.fork_primary] = fork_counts.get(r.fork_primary, 0) + 1

    print(f"\n{'='*70}")
    print(f"FIRM MODEL MONTE CARLO RESULTS  (n={n} iterations){f': {profile_name}' if profile_name else ''}")
    print(f"{'='*70}")
    print(f"\nNote: Varies both market parameters AND firm profile characteristics.")
    print(f"Shows range of firm outcomes given uncertainty in firm type and market.")

    print(f"\n── HEADCOUNT INDEX DISTRIBUTION ─────────────────────────────────")
    print(f"  {'':30}  {'P10':>8}  {'P25':>8}  {'P50':>8}  {'P75':>8}  {'P90':>8}")
    print(f"  {'':30}  {'----':>8}  {'----':>8}  {'----':>8}  {'----':>8}  {'----':>8}")

    def row(label, vals, fmt=".3f"):
        print(f"  {label:<30}  {_pct(vals,10):>8{fmt}}  {_pct(vals,25):>8{fmt}}  "
              f"{_pct(vals,50):>8{fmt}}  {_pct(vals,75):>8{fmt}}  {_pct(vals,90):>8{fmt}}")

    row("Peak employment (firm)", peaks)
    row("Final employment yr10 (firm)", finals)
    row("Final junior index", juniors)
    row("Final senior index", seniors)
    row("Final market index (for ref)", market_finals)

    if beys:
        row("Break-even year (when declined)", beys, ".0f")
    print(f"  {'Headcount never declines':30}  {bey_nevers/n:>7.1%} of runs")

    print(f"\n── VERDICTS ─────────────────────────────────────────────────────")
    pct_above = sum(1 for r in results if r.final_employment > 1.0) / n
    pct_harvest = sum(1 for r in results if r.final_employment < 0.85) / n
    pct_expand = sum(1 for r in results if r.final_employment > 1.30) / n
    print(f"  Final headcount > baseline:    {pct_above:.1%} of runs")
    print(f"  Final headcount > 1.30× (expand):  {pct_expand:.1%} of runs")
    print(f"  Final headcount < 0.85× (harvest): {pct_harvest:.1%} of runs")

    pct_senior_above_junior = sum(
        1 for r in results if r.final_senior > r.final_junior
    ) / n
    print(f"  Senior outperforms junior:     {pct_senior_above_junior:.1%} of runs")

    print(f"\n── MANAGEMENT FORK DISTRIBUTION ─────────────────────────────────")
    for fork in ["HARVEST", "REINVEST", "EXPAND", "IMPROVE"]:
        pct = fork_counts.get(fork, 0) / n
        bar = "█" * int(pct * 30)
        print(f"  {fork:<10}  {pct:>6.1%}  {bar}")

    print(f"\n── SENIOR vs JUNIOR GAP ─────────────────────────────────────────")
    gaps = [r.final_senior - r.final_junior for r in results]
    row("Senior - Junior gap", gaps)
    print(f"  Senior > Junior in {pct_senior_above_junior:.1%} of runs")
    print(f"  (Positive gap = senior employment rises relative to junior)")

    print(f"\n{'='*70}")
