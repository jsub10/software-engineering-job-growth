# Agentic Coding Labor Model v4

Two explanations are provided:
- `docs/model_explanation_detailed.md` — full technical explanation for researchers and analysts
- `docs/model_explanation_simple.md` — plain-language explanation for sharing with others

## What's New in v4

Four structural corrections to the demand model plus three firm model corrections:

**Backlog: dynamic stock with equilibrium**
Backlog never exhausts to zero. It has ongoing inflows (new work, Parkinson's Law,
agentic expansion of feasible projects) and outflows (completion). The equilibrium
backlog settles where inflow = outflow; productivity gains shift equilibrium downward
but Parkinson's Law partially offsets this.

**Technical debt: dynamic stock with AI premium**
Debt accumulates with every feature shipped, and AI-generated code creates ~35% more
debt per line (CMU SEI 2024). Debt feeds back into productivity as a drag. The IMPROVE
fork in the firm model uses extra debt focus to deliberately pay it down.

**Underserved markets: depleting penetration stock**
Once unlocked by sufficient cost reduction, the underserved market depletes as it is
penetrated. Demand from this source exhausts rather than growing indefinitely.

**Induced demand: finite Bass diffusion**
New software categories have a total size (parameter). They emerge via Bass diffusion,
reach peak penetration, and stabilize. Total lifetime induced demand is bounded.

**Aggregate demand ceiling**
After all components are summed, a smooth tanh ceiling prevents demand from exceeding
3x baseline — reflecting the Baumol constraint that complements become binding.

**Firm model: revenue saturation**
Revenue growth decays logistically from its current rate toward a long-run rate,
governed by current_market_penetration. High penetration → fast decay.

**Firm model: organizational absorption cap**
EXPAND strategy capped at 35% annual headcount growth — engineering organizations
cannot hire and productively onboard faster than this.

**Firm model: IMPROVE branch**
Fourth fork. Firms use productivity gains for quality rather than quantity.
Driven by high technical debt, regulated industries, legacy modernization, high penetration.

## Project Structure

```
agentic-labor-model-v4/
├── README.md
├── requirements.txt
├── run.py
├── CLAUDE.md                         ← Claude Code instructions
├── docs/
│   ├── model_explanation_detailed.md ← Full technical explanation
│   └── model_explanation_simple.md  ← Plain-language explanation for sharing
├── config/
│   ├── market_params.yaml
│   └── scenarios.yaml
├── market_model/
│   ├── core/
│   │   ├── breakeven.py              ← Primary output: break-even analysis
│   │   ├── demand_stocks.py          ← Dynamic backlog + tech debt stocks (v4 core)
│   │   ├── demand_saturation.py      ← Underserved, induced demand, ceiling (v4 core)
│   │   ├── model.py
│   │   ├── exogenous.py
│   │   ├── scenario_runner.py
│   │   └── uncertainty.py
│   └── diffusion/
│       └── bass.py
├── firm_model/
│   ├── core/
│   │   └── firm_model.py             ← Four-way fork with v4 corrections
│   └── profiles/
│       ├── enterprise_saas.yaml
│       ├── regulated_bank.yaml
│       ├── consumer_startup.yaml
│       └── manufacturing_it.yaml
├── output/
│   ├── charts.py
│   ├── tables.py
│   └── reports.py
└── tests/
    └── test_v4.py                    ← 31 tests
```

## Quickstart

```bash
pip install -r requirements.txt
python run.py                                      # base scenario
python run.py --scenarios all                      # all 8 scenarios
python run.py --scenario base --exogenous ai_boom
python run.py --sensitivity labor.g_tools          # sensitivity analysis
python run.py --monte-carlo --iterations 1000
python run.py --scenarios all --output all         # save charts + tables + report
python run.py --firm firm_model/profiles/enterprise_saas.yaml
python run.py --firm-compare
python -m pytest tests/ -v
```

## Key Model Insight from v4

The base scenario now shows:
- Years 1-5: Jevons HOLDS (demand > productivity)
  - Backlog release and tech debt remediation front-load demand
  - Adoption still ramping; productivity muted early
- Years 6-10: Jevons FAILS (productivity > demand)
  - Backlog reaches new equilibrium; demand normalizes
  - Adoption reaches critical mass; productivity compounds

**The near term looks better for engineers than the long term.**
This is the most important structural prediction from v4, and it only
emerges because backlog and debt are modeled as dynamic stocks, not
one-time releases.

## New v4 Firm Profile Fields

Two new required fields:
  `long_run_growth_rate`: where revenue growth decays toward (default ~0.06)
  `current_market_penetration`: fraction of TAM currently captured (0.0-1.0)

These determine how fast the revenue saturation kicks in for EXPAND firms.
