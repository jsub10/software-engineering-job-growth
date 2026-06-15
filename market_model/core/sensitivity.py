"""
Break-even sensitivity analysis.

Shows how the break-even year (first year employment starts declining)
moves as the most important uncertain parameters change.

The break-even year is the single most decision-relevant output:
  - It tells practitioners how long the "window" of rising employment lasts
  - It identifies what to watch to know whether the window is closing sooner

KEY PARAMETERS FOR SENSITIVITY:
  g_tools:               Tool improvement rate (NO EMPIRICAL BASIS; dominant driver)
  parkinson_coefficient: Scope expansion rate (NO EMPIRICAL BASIS; demand driver)
  alpha_maturation_years: How fast tools shift from METR drag to routine gain (LOW confidence)
  consumer_capture_rate: Pass-through of savings to market (LOW confidence)
  adoption.q:            Bass imitation coefficient (LOW confidence)
  cognitive_scope_max:   Ceiling on cognitive assistance (NO EMPIRICAL BASIS)

OUTPUT FORMAT:
  A table showing break-even year across a grid of key parameters.
  Each cell = (peak_year, break_even_year, final_employment_index).

WHY THIS IS THE RIGHT PRIMARY SENSITIVITY OUTPUT:
  The employment index at any single year is less informative than the
  trajectory shape. Two models can agree on year-5 employment but disagree
  sharply on whether employment is still rising or already falling.
  The break-even year captures this directional information.
"""

import copy
from typing import Dict, List, Optional, Tuple

import yaml


def load_params(path: str = "config/market_params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _run_with_override(base_params: dict, overrides: dict):
    """Run model with parameter overrides and return (peak_yr, bey, final_emp)."""
    from market_model.core.model import MarketModel
    p = copy.deepcopy(base_params)
    for path, value in overrides.items():
        keys = path.split(".")
        target = p
        for k in keys[:-1]:
            target = target[k]
        target[keys[-1]] = value
    result = MarketModel(p).run()
    bey = result.break_even_year
    return (result.peak_year, bey, result.final_employment_index)


def run_breakeven_sensitivity(
    params_path: str = "config/market_params.yaml"
) -> Dict[str, list]:
    """
    Run sensitivity analysis on the break-even year across key parameters.
    Returns a dict mapping parameter name → list of (value, peak_yr, bey, final_emp).
    """
    base = load_params(params_path)

    # Parameter ranges: (param_path, values, label)
    # Ordered by estimated importance (most impactful first)
    SENSITIVITY_PARAMS = [
        (
            "labor.g_tools",
            [0.10, 0.15, 0.20, 0.25, 0.30, 0.40],
            "Tool improvement rate (g_tools)",
            "NO EMPIRICAL BASIS — most impactful uncertain parameter",
        ),
        (
            "demand.parkinson_coefficient",
            [0.10, 0.20, 0.25, 0.30, 0.40, 0.50],
            "Parkinson scope-expansion coefficient",
            "NO EMPIRICAL BASIS — how much new scope fills freed capacity",
        ),
        (
            "labor.alpha_maturation_years",
            [2.0, 3.0, 4.0, 5.0, 7.0, 10.0],
            "Alpha maturation years (METR drag → routine gain)",
            "LOW confidence — structural assumption about tool improvement pace",
        ),
        (
            "context.annual_cost_reduction_rate",
            [0.05, 0.08, 0.12, 0.18, 0.25, 0.35],
            "Annual unit cost reduction rate",
            "NO EMPIRICAL BASIS — most consequential macro parameter",
        ),
        (
            "adoption.q",
            [0.15, 0.25, 0.38, 0.50, 0.65],
            "Bass imitation coefficient (adoption speed)",
            "LOW confidence — fitted to Copilot 2021-2024",
        ),
        (
            "cognitive.cognitive_scope_max",
            [0.0, 0.15, 0.30, 0.45, 0.60],
            "Cognitive scope maximum (fraction of cognitive work AI-assisted)",
            "NO EMPIRICAL BASIS — V5 addition",
        ),
    ]

    results = {}
    for param_path, values, label, confidence_note in SENSITIVITY_PARAMS:
        param_results = []
        for v in values:
            peak_yr, bey, final_emp = _run_with_override(base, {param_path: v})
            bey_str = str(bey) if bey else "never"
            param_results.append((v, peak_yr, bey_str, final_emp))
        results[param_path] = {
            "label": label,
            "confidence_note": confidence_note,
            "values": param_results,
        }

    return results


def print_sensitivity_table(results: Dict) -> None:
    """Print break-even sensitivity table as the primary output."""
    print(f"\n{'='*80}")
    print("BREAK-EVEN SENSITIVITY ANALYSIS")
    print("How does the break-even year move as key parameters change?")
    print(f"{'='*80}")
    print("Break-even year = first year employment starts declining from peak.")
    print("'never' = employment still rising at end of simulation (year 10).")
    print()

    for param_path, data in results.items():
        print(f"  {data['label']}")
        print(f"  [{data['confidence_note']}]")
        print(f"  {'Value':>8}  {'Peak Yr':>8}  {'Break-Even':>11}  {'Final Emp':>10}  {'Direction'}") 
        print(f"  {'-'*60}")
        for v, peak_yr, bey_str, final_emp in data["values"]:
            direction = "↑ RISING" if bey_str == "never" else f"↓ peaks yr{peak_yr}"
            final_str = f"{final_emp:.3f}×"
            marker = " ← base" if abs(v - _get_base_value(param_path)) < 0.001 else ""
            print(f"  {v:>8.2f}  {peak_yr:>8}  {bey_str:>11}  {final_str:>10}  {direction}{marker}")
        print()

    print("KEY INSIGHT: g_tools and parkinson_coefficient are the dominant drivers.")
    print("The break-even year is highly sensitive to both. Neither has empirical calibration.")
    print(f"{'='*80}")


def _get_base_value(param_path: str) -> float:
    """Get the base value for a parameter (for marking in table)."""
    base_values = {
        "labor.g_tools": 0.20,
        "demand.parkinson_coefficient": 0.25,
        "labor.alpha_maturation_years": 5.0,
        "context.annual_cost_reduction_rate": 0.12,
        "adoption.q": 0.38,
        "cognitive.cognitive_scope_max": 0.30,
    }
    return base_values.get(param_path, -999)


def run_crossplot(
    params_path: str = "config/market_params.yaml",
) -> None:
    """
    Cross-plot: break-even year as function of two key parameters simultaneously.
    g_tools × parkinson_coefficient — the two dominant uncertain drivers.
    """
    base = load_params(params_path)

    g_tools_values = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
    parkinson_values = [0.15, 0.25, 0.35, 0.45]

    print(f"\n{'='*75}")
    print("CROSS-PLOT: Break-Even Year = f(g_tools, parkinson_coefficient)")
    print("(Both parameters have NO empirical basis — this shows full uncertainty range)")
    print(f"{'='*75}")
    print(f"  g_tools \\ parkinson→  ", end="")
    for pc in parkinson_values:
        print(f"  pc={pc:.2f}", end="")
    print()
    print(f"  {'─'*65}")

    for gt in g_tools_values:
        print(f"  g_tools={gt:.2f}          ", end="")
        for pc in parkinson_values:
            _, bey, _ = _run_with_override(base, {
                "labor.g_tools": gt,
                "demand.parkinson_coefficient": pc,
            })
            bey_str = f"yr{bey:>2}" if bey else "never"
            marker = " *" if (abs(gt - 0.20) < 0.001 and abs(pc - 0.25) < 0.001) else "  "
            print(f"  {bey_str:>5}{marker}", end="")
        print()

    print(f"\n  * = current base parameters (g_tools=0.20, parkinson=0.25)")
    print(f"  Interpretation: cells to upper-left = faster break-even")
    print(f"                  cells to lower-right = slower break-even")
    print(f"{'='*75}")
