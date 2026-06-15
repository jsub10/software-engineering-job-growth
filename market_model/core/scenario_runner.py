"""Scenario runner for market model v4."""
import copy, yaml
from typing import Dict, Optional
from market_model.core.model import MarketModel, MarketModelResult
from market_model.core.exogenous import ExogenousParams, EXOGENOUS_PRESETS
from market_model.diffusion.bass import BassParams, ADOPTION_PRESETS


def load_params(path="config/market_params.yaml"):
    with open(path) as f: return yaml.safe_load(f)

def load_scenarios(path="config/scenarios.yaml"):
    with open(path) as f: return yaml.safe_load(f)

def deep_merge(base, overrides):
    result = copy.deepcopy(base)
    for k, v in overrides.items():
        if isinstance(v, dict) and k in result and isinstance(result[k], dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def run_scenario(scenario_name, params_path="config/market_params.yaml",
                 scenarios_path="config/scenarios.yaml", exogenous_name=None,
                 adoption_preset=None, cli_overrides=None):
    params = load_params(params_path)
    scenarios = load_scenarios(scenarios_path)
    if scenario_name != "base":
        overrides = scenarios["scenarios"].get(scenario_name, {}).get("overrides", {})
        params = deep_merge(params, overrides)
    if cli_overrides:
        for override in cli_overrides:
            path, value = override.split("=", 1)
            keys = path.strip().split(".")
            try: value = float(value)
            except ValueError: pass
            target = params
            for k in keys[:-1]: target = target[k]
            target[keys[-1]] = value
    exog = EXOGENOUS_PRESETS.get(exogenous_name) if exogenous_name else None
    bass = ADOPTION_PRESETS.get(adoption_preset) if adoption_preset else None
    return MarketModel(params).run(scenario_name, exog, bass)


def run_all_scenarios(params_path="config/market_params.yaml",
                      scenarios_path="config/scenarios.yaml", exogenous_name=None):
    scenarios = load_scenarios(scenarios_path)
    return {name: run_scenario(name, params_path, scenarios_path, exogenous_name)
            for name in scenarios["scenarios"]}


def print_primary_output_table(all_results: Dict[str, MarketModelResult]) -> None:
    """
    PRIMARY OUTPUT TABLE.
    Shows the four most important numbers for each scenario.
    """
    n = list(all_results.values())[0].n_years
    print(f"\n{'='*90}")
    print(f"PRIMARY OUTPUT: EMPLOYMENT TRAJECTORY (v4)")
    print(f"{'='*90}")
    print(f"{'Scenario':<22} {'Peak':>7} {'PeakYr':>7} {'BreakEven':>10} {'Final':>7} {'Exog':>6}")
    print(f"{'':22} {'EmpIdx':>7} {'':>7} {'Year':>10} {'EmpIdx':>7} {'Mult':>6}")
    print("-" * 65)
    for name, run in all_results.items():
        bey = run.break_even_year
        bey_str = f"yr {bey}" if bey else "never"
        print(f"{name:<22} {run.peak_employment_index:>7.3f} {run.peak_year:>7} "
              f"{bey_str:>10} {run.final_employment_index:>7.3f} "
              f"{run.exogenous_multiplier:>6.3f}")
    print("-" * 65)
    print("Peak EmpIdx: max employment above baseline (1.0 = no change)")
    print("PeakYr:      year employment reaches peak")
    print("BreakEven:   year employment starts declining from peak")
    print("Final EmpIdx: employment in the final year (may be above or below baseline)")
    print(f"{'='*90}")

    print(f"\n{'='*90}")
    print(f"BREAK-EVEN MARGIN TABLE: g_demand vs g_productivity (final year)")
    print(f"{'='*90}")
    print(f"{'Scenario':<22} {'Demand':>9} {'Prodctvy':>9} {'Margin':>9} {'Flip@':>9} "
          f"{'Backlog':>8} {'Debt%':>7}")
    print("-" * 80)
    for name, run in all_results.items():
        be = run.breakeven[-1]
        print(f"{name:<22} {be.g_demand:>9.2%} {be.g_productivity:>9.2%} "
              f"{be.margin:>+9.2%} {be.productivity_to_flip:>9.2%} "
              f"{be.backlog_level:>8.1f}mo {be.debt_level:>7.1f}%")
    print("-" * 80)
    print("Margin > 0: employment still rising in the final year")
    print("Margin < 0: employment falling in the final year")
    print("Flip@: productivity growth rate that would flip employment direction")
    print(f"{'='*90}")
