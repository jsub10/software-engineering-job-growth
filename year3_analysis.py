"""One-off: extract year-3 demand-vs-productivity statistics from the
identical Monte Carlo draw used by `run.py --monte-carlo --iterations 1000`.

Replicates run_market_monte_carlo's draw loop EXACTLY (same seed, same
parameter iteration order) so results match the published report, but
records the break-even entry for year 3 instead of only year 10.
"""
import copy, random
from market_model.core.scenario_runner import load_params
from market_model.core.monte_carlo import MARKET_MC_PARAMS, _set_nested
from market_model.core.model import MarketModel

N = 1000
TARGET_YEAR = 3

base_params = load_params("config/market_params.yaml")
rng = random.Random(42)  # same seed as run_market_monte_carlo default

margins_yr3 = []      # margin = g_demand - g_productivity  (>0 => demand wins, Jevons)
prod_yr3 = []
demand_yr3 = []

for i in range(N):
    p = copy.deepcopy(base_params)
    for path, (lo, hi) in MARKET_MC_PARAMS.items():
        if "consumer_capture_rate." in path:
            segment = path.split(".")[-1]
            p["market"]["consumer_capture_rate"][segment] = rng.uniform(lo, hi)
        else:
            _set_nested(p, path, rng.uniform(lo, hi))
    try:
        run = MarketModel(p).run(scenario_name=f"mc_{i}")
        yr3 = next((r for r in run.breakeven if r.year == TARGET_YEAR), None)
        if yr3 is None:
            continue
        margins_yr3.append(yr3.margin)
        prod_yr3.append(yr3.g_productivity)
        demand_yr3.append(yr3.g_demand)
    except Exception:
        pass

n = len(margins_yr3)

# "productivity grows as fast or faster than demand" => g_prod >= g_demand
# => margin = g_demand - g_prod <= 0
prod_ge_demand = sum(1 for m in margins_yr3 if m <= 0)
prod_strictly_faster = sum(1 for m in margins_yr3 if m < 0)
demand_strictly_faster = sum(1 for m in margins_yr3 if m > 0)

def pct(vals, q):
    s = sorted(vals); return s[max(0, min(len(s)-1, int(q/100*len(s))))]

print(f"\n=== YEAR {TARGET_YEAR} ANALYSIS (n={n} successful runs) ===\n")
print(f"Productivity >= demand (prod as fast or faster): {prod_ge_demand}/{n} = {prod_ge_demand/n:.1%}")
print(f"  of which strictly faster (prod > demand):      {prod_strictly_faster}/{n} = {prod_strictly_faster/n:.1%}")
print(f"Demand strictly faster (Jevons holds):           {demand_strictly_faster}/{n} = {demand_strictly_faster/n:.1%}")
print()
print(f"Median demand growth yr{TARGET_YEAR}:       {pct(demand_yr3,50)*100:.1f}%/yr")
print(f"Median productivity growth yr{TARGET_YEAR}: {pct(prod_yr3,50)*100:.1f}%/yr")
print(f"Median margin (D-P) yr{TARGET_YEAR}:        {pct(margins_yr3,50)*100:.1f}%/yr")
print(f"Margin P10/P25/P75/P90: {pct(margins_yr3,10)*100:.1f} / {pct(margins_yr3,25)*100:.1f} / "
      f"{pct(margins_yr3,75)*100:.1f} / {pct(margins_yr3,90)*100:.1f}  (%/yr)")
