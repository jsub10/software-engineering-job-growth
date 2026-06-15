# Agentic Coding Labor Model v4

## Purpose
Estimates the effect of agentic coding on software engineer employment.
PRIMARY output: break-even analysis (what productivity growth flips employment direction).
SECONDARY output: employment index (lower confidence).

## Architecture
- `market_model/core/demand_stocks.py` — CORE V4: dynamic backlog + tech debt stocks
- `market_model/core/demand_saturation.py` — CORE V4: underserved markets, induced demand, ceiling
- `market_model/core/breakeven.py` — primary output computation
- `market_model/core/model.py` — orchestrates a full run
- `market_model/diffusion/bass.py` — Bass diffusion (tool adoption + induced demand)
- `firm_model/core/firm_model.py` — four-way fork (Harvest/Reinvest/Expand/Improve)
- `config/market_params.yaml` — all parameters with confidence flags in comments
- `docs/model_explanation_detailed.md` — full technical explanation

## How to run
```bash
pip install -r requirements.txt
python run.py                          # base scenario
python run.py --scenarios all          # all scenarios
python run.py --firm-compare           # all firm profiles
python run.py --monte-carlo            # Monte Carlo
python run.py --sensitivity labor.g_tools
python -m pytest tests/ -v
```

## Key design decisions — do not change without understanding why

1. Backlog and technical debt are DYNAMIC STOCKS with inflows and outflows.
   They never go to zero. Inflows include Parkinson's Law (scope expands with capacity)
   and AI debt premium (AI code creates more debt per line).

2. Underserved markets DEPLETE as penetrated. Induced demand has finite total size.
   Both exhaust over time rather than growing indefinitely.

3. Aggregate demand ceiling uses tanh saturation: D_sat = D_max × tanh(D/D_max).
   This passes through below D_max and asymptotes above it.

4. Firm model has FOUR forks: Harvest, Reinvest, Expand, Improve.
   IMPROVE is new in v4: productivity gains absorbed into quality, not quantity.

5. Revenue growth in EXPAND firms saturates logistically toward long_run_growth_rate,
   driven by current_market_penetration.

6. Organizational absorption cap: max 35%/yr headcount growth from EXPAND.

7. Break-even is primary output. Employment index is secondary.
   The asymmetry (demand better calibrated than productivity) is intentional.

## Parameters with NO empirical basis — must be varied in sensitivity analysis
parkinson_coefficient, agentic_expansion_rate, g_tools, f_verify,
underserved_fraction, induced_market_size, annual_cost_reduction_rate, phi

## Parameters with strong empirical grounding
tech_debt_initial_pct: 0.40 (McKinsey 2023, SO 2024 N=65,437)
alpha_experienced: -0.19 (METR RCT, Becker et al. 2025)
ai_debt_premium: 0.35 (CMU SEI 2024)
market baseline growth: 8%/yr (BLS Nov 2025)

## Adding a new scenario
Add to config/scenarios.yaml under scenarios: with overrides: block.
Only specify parameters that differ from base.

## Adding a firm profile
Copy any existing profile in firm_model/profiles/.
Required new v4 fields: long_run_growth_rate, current_market_penetration.
Valid industries: consumer_tech, enterprise_saas, fintech, healthcare, manufacturing, government, general.
