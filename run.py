#!/usr/bin/env python3
"""
Agentic Coding Labor Model v4

PRIMARY OUTPUT: Break-even analysis with dynamic demand stocks
SECONDARY OUTPUT: Employment index

Market model:
    python run.py                                    # base scenario
    python run.py --scenarios all                    # all scenarios
    python run.py --scenario jevons_holds --exogenous ai_boom
    python run.py --scenario base --set demand.parkinson_coefficient=0.6
    python run.py --sensitivity labor.g_tools
    python run.py --monte-carlo --iterations 1000
    python run.py --scenarios all --output all

Firm model:
    python run.py --firm firm_model/profiles/enterprise_saas.yaml
    python run.py --firm-compare
    python run.py --firm-compare --scenario jevons_fails
"""

import argparse, os, sys, yaml


def parse_args():
    p = argparse.ArgumentParser(description="Agentic Labor Model v4", epilog=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scenario", default="base")
    p.add_argument("--scenarios", default=None)
    p.add_argument("--exogenous", default=None)
    p.add_argument("--adoption", default=None)
    p.add_argument("--set", dest="overrides", action="append", default=[])
    p.add_argument("--output", default="print")
    p.add_argument("--monte-carlo", action="store_true")
    p.add_argument("--iterations", type=int, default=1000)
    p.add_argument("--sensitivity", metavar="PARAM", default=None)
    p.add_argument("--firm", metavar="PROFILE_YAML", default=None)
    p.add_argument("--firm-compare", action="store_true")
    p.add_argument("--firm-monte-carlo", action="store_true",
                   help="Monte Carlo for firm model (varies both market and firm params)")
    p.add_argument("--breakeven-sensitivity", action="store_true",
                   help="Show break-even year sensitivity across key parameters")
    p.add_argument("--crossplot", action="store_true",
                   help="Cross-plot break-even year: g_tools × parkinson_coefficient")
    p.add_argument("--params", default="config/market_params.yaml")
    p.add_argument("--scenarios-config", default="config/scenarios.yaml")
    return p.parse_args()


def run_market(args):
    from market_model.core.scenario_runner import (
        run_scenario, run_all_scenarios, print_primary_output_table, load_params
    )
    from market_model.core.model import MarketModel
    from market_model.core.uncertainty import UNCERTAIN_PARAMS

    for d in ["output/charts", "output/tables", "output/reports"]:
        os.makedirs(d, exist_ok=True)

    if args.breakeven_sensitivity:
        from market_model.core.sensitivity import run_breakeven_sensitivity, print_sensitivity_table
        print("Running break-even sensitivity analysis (6 parameters × 5-6 values each)...")
        results = run_breakeven_sensitivity(args.params)
        print_sensitivity_table(results)
        return

    if args.crossplot:
        from market_model.core.sensitivity import run_crossplot
        run_crossplot(args.params)
        return

    if args.monte_carlo:
        from market_model.core.monte_carlo import run_market_monte_carlo, print_market_mc_report
        print(f"\nRunning comprehensive market Monte Carlo ({args.iterations} iterations)...")
        print("Varying all uncertain parameters simultaneously.")
        params = load_params(args.params)
        mc_results = run_market_monte_carlo(params, n_iterations=args.iterations)
        print_market_mc_report(mc_results)
        from output.mc_report import write_market_mc_report
        report_path = write_market_mc_report(
            mc_results, n_years=params["context"]["simulation_years"],
            n_iterations=args.iterations, params_label=args.params,
        )
        print(f"\nDetailed report saved: {report_path}")
        if "charts" in args.output or args.output == "all":
            legacy = [{"employment_index": r.final_employment,
                        "g_demand": r.g_demand_yr10,
                        "g_productivity": r.g_productivity_yr10,
                        "margin": r.margin_yr10} for r in mc_results]
            from output.charts import plot_monte_carlo
            plot_monte_carlo(legacy, "output/charts/monte_carlo.png")
            print("Chart saved: output/charts/monte_carlo.png")
        return

    if args.sensitivity:
        if args.sensitivity not in UNCERTAIN_PARAMS:
            print("Unknown param. Available:\n" + "\n".join(f"  {k}" for k in UNCERTAIN_PARAMS))
            sys.exit(1)
        lo, hi = UNCERTAIN_PARAMS[args.sensitivity]
        values = [lo + i*(hi-lo)/9 for i in range(10)]
        params = load_params(args.params)
        results = MarketModel(params).sensitivity_analysis(args.sensitivity, values)
        print(f"\nSensitivity: {args.sensitivity}")
        print(f"{'Value':>10}  {'Demand':>9}  {'Prod':>9}  {'Margin':>9}  "
              f"{'EmpIdx':>9}  {'Backlog':>8}  {'Debt%':>7}  {'Jevons':>7}")
        print("-" * 82)
        for v, r in results.items():
            jevons = "HOLDS" if r["jevons_holds"] else "FAILS"
            print(f"{v:>10.3f}  {r['g_demand']:>9.2%}  {r['g_productivity']:>9.2%}  "
                  f"{r['margin']:>+9.2%}  {r['employment_index']:>9.3f}  "
                  f"{r['backlog_yr10']:>8.1f}  {r['debt_yr10']:>7.1f}  {jevons:>7}")
        return

    if args.scenarios == "all":
        print("Running all scenarios...")
        all_results = run_all_scenarios(args.params, args.scenarios_config, args.exogenous)
        print_primary_output_table(all_results)
        _print_secondary(all_results)
        _handle_output(args, all_results)
    else:
        result = run_scenario(args.scenario, args.params, args.scenarios_config,
                              args.exogenous, args.adoption, args.overrides)
        all_results = {args.scenario: result}
        _print_single(result)
        _handle_output(args, all_results)


def _print_single(run):
    n = run.n_years
    bey = run.break_even_year
    bey_str = f"year {bey}" if bey else "never within simulation"

    print(f"\n{'='*70}")
    print(f"PRIMARY OUTPUT — EMPLOYMENT TRAJECTORY: {run.scenario_name}")
    print(f"{'='*70}")
    print(f"Exogenous multiplier:  {run.exogenous_multiplier:.3f}")
    print(f"")
    print(f"  Peak employment:     {run.peak_employment_index:.3f}× baseline  (year {run.peak_year})")
    print(f"  Break-even year:     {bey_str}  (first year employment starts declining)")
    print(f"  Final employment:    {run.final_employment_index:.3f}× baseline  (year {n})")
    print(f"")
    print(f"Interpretation:")
    if run.peak_employment_index > 1.0:
        above = run.peak_employment_index - 1.0
        print(f"  Engineers peak at {above:.1%} above baseline ({run.peak_employment_index:.3f}×) in year {run.peak_year}.")
    if bey:
        print(f"  Employment starts declining in year {bey}.")
    if run.final_employment_index >= 1.0:
        above = run.final_employment_index - 1.0
        print(f"  By year {n}, still {above:.1%} above baseline ({run.final_employment_index:.3f}×).")
    else:
        print(f"  By year {n}, {1.0-run.final_employment_index:.1%} below baseline.")

    print(f"")
    print(f"{'='*70}")
    print(f"BREAK-EVEN MARGIN DETAIL (what drives the trajectory)")
    print(f"{'='*70}")
    print(f"  Demand > Productivity → employment rising  (Jevons holds)")
    print(f"  Demand < Productivity → employment falling (Jevons fails)")
    print(f"")
    print(f"  {'Yr':>3}  {'Demand':>8}  {'Prodctvy':>9}  {'Margin':>8}  {'Adopt':>6}  {'Status':>12}")
    print(f"  {'-'*60}")
    for be in run.breakeven:
        status = "rising ▲" if be.jevons_holds else "falling ▼"
        print(f"  {be.year:>3}  {be.g_demand:>8.2%}  {be.g_productivity:>9.2%}  "
              f"{be.margin:>+8.2%}  {be.adoption_fraction:>6.0%}  {status:>12}")

    final = run.breakeven[-1]
    print(f"")
    print(f"  Year {n} demand decomposition:")
    for k, v in final.g_demand_components.items():
        if abs(v) > 0.0001:
            print(f"    {k:<20} {v:>+.2%}/yr")
    print(f"    {'TOTAL':<20} {final.g_demand:>+.2%}/yr")
    print(f"")
    print(f"  Year {n} productivity decomposition:")
    for k, v in final.g_productivity_components.items():
        if abs(v) > 0.0001:
            tag = "  ← V5 cognitive" if k == "cognitive_tasks" else ""
            print(f"    {k:<22} {v:>+.2%}/yr{tag}")
    print(f"    {'TOTAL':<22} {final.g_productivity:>+.2%}/yr")
    print(f"  Cognitive scope (yr {n}): {final.cognitive_scope:.1%} of cognitive work AI-assisted")
    print(f"  Cognitive gain (yr {n}):  {final.cognitive_gain:>+.2%}/yr  (NO EMPIRICAL BASIS)")
    print(f"  To flip direction:    productivity must {'fall below' if final.jevons_holds else 'stay below'} "
          f"{final.productivity_to_flip:.2%}/yr")
    print(f"  Stocks: backlog {final.backlog_level:.1f}mo, debt {final.debt_level:.1f}%")

    print(f"")
    print(f"{'='*70}")
    print(f"SECONDARY: Employment Index by Year (lower confidence)")
    print(f"{'='*70}")
    for yr, idx in sorted(run.employment_index.items()):
        delta = idx - 1.0
        bar = ("+" * int(abs(delta) * 30)) if delta >= 0 else ("-" * int(abs(delta) * 30))
        arrow = "▲" if idx > 1.0 else "▼" if idx < 1.0 else "—"
        print(f"  Year {yr:2d}: {idx:.3f} {arrow}  {bar}")
    bt = run.employment_by_tier.get(n, {})
    print(f"  Year {n} tiers: Junior={bt.get('junior',0):.3f}  "
          f"Mid={bt.get('mid',0):.3f}  Senior={bt.get('senior',0):.3f}")


def _print_secondary(all_results):
    n = list(all_results.values())[0].n_years
    print(f"\nSECONDARY: Employment Index (Year {n})")
    print(f"{'Scenario':<22} {'EmpIdx':>8} {'Junior':>8} {'Mid':>8} {'Senior':>8}")
    print("-" * 58)
    for nm, run in all_results.items():
        emp = run.employment_index.get(n, 1.0)
        bt = run.employment_by_tier.get(n, {})
        print(f"{nm:<22} {emp:>8.3f} {bt.get('junior',0):>8.3f} "
              f"{bt.get('mid',0):>8.3f} {bt.get('senior',0):>8.3f}")


def _print_mc(results):
    indices = [r["employment_index"] for r in results]
    margins = [r["margin"] for r in results]
    n = len(results)
    si = sorted(indices); sm = sorted(margins)
    print(f"\n{'='*55}")
    print(f"PRIMARY: Break-Even Margin ({n} iterations)")
    print(f"  Mean: {sum(margins)/n:>+.3%}/yr  Median: {sm[n//2]:>+.3%}/yr")
    print(f"  P10:  {sm[n//10]:>+.3%}/yr  P90: {sm[9*n//10]:>+.3%}/yr")
    pct = sum(1 for m in margins if m > 0) / n
    print(f"  Demand > Productivity in {pct:.1%} of draws")
    print(f"\nSECONDARY: Employment Index")
    print(f"  Mean: {sum(indices)/n:.3f}  Median: {si[n//2]:.3f}")
    print(f"  P10:  {si[n//10]:.3f}  P90: {si[9*n//10]:.3f}")


def _handle_output(args, all_results):
    if args.output == "print": return
    if "charts" in args.output or args.output == "all":
        from output.charts import plot_breakeven_fan, plot_employment_index, plot_stocks
        plot_breakeven_fan(all_results, "output/charts/breakeven_fan.png")
        plot_employment_index(all_results, "output/charts/employment_index.png")
        plot_stocks(all_results, "output/charts/demand_stocks.png")
        print("Charts saved: output/charts/")
    if "tables" in args.output or args.output == "all":
        from output.tables import export_all
        export_all(all_results, "output/tables/")
        print("Tables saved: output/tables/")
    if "report" in args.output or args.output == "all":
        from output.reports import generate_report
        generate_report(all_results, "output/reports/report.md")
        print("Report saved: output/reports/report.md")


def run_firm(args):
    from market_model.core.scenario_runner import run_scenario, load_params
    from firm_model.core.firm_model import FirmModel, FirmProfile

    if args.firm_monte_carlo:
        from market_model.core.monte_carlo import run_firm_monte_carlo, print_firm_mc_report
        base_mp = load_params(args.params)
        # Use supplied firm profile as base, or generic default
        if args.firm:
            with open(args.firm) as f:
                base_fp = yaml.safe_load(f)
            profile_name = base_fp.get("name", args.firm)
        else:
            base_fp = {
                "name": "Generic Firm", "industry": "general",
                "current_headcount": 100, "junior_fraction": 0.35,
                "senior_fraction": 0.20, "annual_revenue_usd": 50000000,
                "revenue_growth_rate": 0.10, "long_run_growth_rate": 0.06,
                "current_market_penetration": 0.10,
                "software_is_core_product": True, "build_buy_ratio": 0.80,
                "backlog_months": 6.0, "technical_debt_pct": 35.0,
                "has_legacy_modernization": False,
                "will_pass_savings_to_customers": False,
                "competitive_intensity": "medium",
                "capital_efficiency_pressure": "medium",
                "firm_parkinson_override": None,
                "agentic_adoption_rate": 0.30, "adoption_maturity": "early",
            }
            profile_name = "Generic Firm (population draw)"
        print(f"\nRunning firm Monte Carlo ({args.iterations} iterations): {profile_name}")
        print("Varies both market model parameters and firm profile characteristics.")
        results = run_firm_monte_carlo(
            base_mp, base_fp, n_iterations=args.iterations,
            vary_firm_params=True, vary_market_params=True,
        )
        print_firm_mc_report(results, profile_name)
        from output.mc_report import write_firm_mc_report
        report_path = write_firm_mc_report(
            results, n_years=base_mp["context"]["simulation_years"],
            n_iterations=args.iterations, profile_name=profile_name,
        )
        print(f"\nDetailed report saved: {report_path}")
        return

    market_run = run_scenario(args.scenario, args.params, args.scenarios_config,
                              args.exogenous, args.adoption, args.overrides)
    market_params = load_params(args.params)

    if args.firm_compare:
        profile_dir = "firm_model/profiles"
        yamls = sorted(f for f in os.listdir(profile_dir) if f.endswith(".yaml"))
        firm_data = []
        for fname in yamls:
            with open(os.path.join(profile_dir, fname)) as f:
                data = yaml.safe_load(f)
            profile = FirmProfile(**data)
            firm = FirmModel(profile, market_run, market_params)
            results = firm.run()
            print(firm.summary(results))
            debt_traj = [r.debt_level for r in results]
            firm_data.append((profile.name, results, results[0].fork_weights.primary, debt_traj))
        if "charts" in args.output or args.output == "all":
            from output.charts import plot_firm_comparison
            plot_firm_comparison(firm_data, "output/charts/firm_comparison.png")
    else:
        with open(args.firm) as f:
            data = yaml.safe_load(f)
        profile = FirmProfile(**data)
        firm = FirmModel(profile, market_run, market_params)
        results = firm.run()
        print(firm.summary(results))
        print(f"\nYear-by-year:")
        print(f"  {'Yr':>2}  {'HCIdx':>7}  {'HC':>6}  {'Junior':>7}  "
              f"{'Senior':>7}  {'Debt%':>6}  {'Fork':<10}  {'Market':>7}")
        print(f"  {'--':>2}  {'-----':>7}  {'--':>6}  {'------':>7}  "
              f"{'------':>7}  {'-----':>6}  {'----':<10}  {'------':>7}")
        for r in results:
            print(f"  {r.year:>2}  {r.headcount_index:>7.3f}  "
                  f"{r.headcount_absolute:>6}  {r.junior_index:>7.3f}  "
                  f"{r.senior_index:>7.3f}  {r.debt_level:>6.1f}  "
                  f"{r.fork_weights.primary:<10}  {r.market_index:>7.3f}")


def main():
    args = parse_args()
    if args.firm or args.firm_compare or args.firm_monte_carlo:
        run_firm(args)
    else:
        run_market(args)


if __name__ == "__main__":
    main()
