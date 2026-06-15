# Agentic Coding Labor Model v5

## Purpose
Estimates the effect of agentic coding on software engineer employment,
with explicit modeling of cognitive capability replication.

PRIMARY output: break-even analysis (peak employment, break-even year, final employment).
SECONDARY output: employment index trajectory by tier. The index tracks reduction/increase in software engineers by tenure - junior, middle, senior engineers.

## What's New in V5
Agentic tools don't just automate tasks — they replicate cognitive capabilities:
  - Specification and decomposition (breaking problems into pieces)
  - Context synthesis across large codebases
  - Debugging hypothesis generation
  - Requirements elicitation and formalization

V5 adds three components to model this:
  1. Three-component alpha: alpha_experienced + alpha_routine + alpha_cognitive (NEW)
  2. Cognitive scope expansion: separate from f_auto, grows more slowly
  3. Cognitive leverage in tier adjustments: senior benefits MORE, junior LESS

ALL cognitive parameters have NO EMPIRICAL BASIS. Set cognitive_scope_max=0 to reproduce v4.

## Architecture
- `market_model/core/breakeven.py` — PRIMARY: break-even with cognitive components
- `market_model/core/demand_stocks.py` — Dynamic backlog + tech debt (v4 core)
- `market_model/core/demand_saturation.py` — Underserved markets, induced demand, ceiling
- `market_model/core/model.py` — Orchestrates run; applies cognitive leverage to tiers
- `market_model/diffusion/bass.py` — Bass diffusion for tool adoption
- `firm_model/core/firm_model.py` — Four-way fork + cognitive leverage in tier adjustments
- `config/market_params.yaml` — All parameters; cognitive section at bottom
- `docs/v5_cognitive_additions.md` — Why and how cognitive components work

## How to run
```bash
pip install -r requirements.txt
python run.py                                    # base (with v5 cognitive)
python run.py --scenarios all                    # all scenarios
python run.py --scenario cognitive_optimistic    # aggressive cognitive scenario
python run.py --scenario cognitive_off           # reproduces v4 exactly
python run.py --firm firm_model/profiles/enterprise_saas.yaml
python run.py --firm-compare
python run.py --monte-carlo --iterations 1000   # writes a timestamped report to output/reports/
python run.py --firm-monte-carlo --iterations 1000  # firm report to output/reports/
python run.py --combined-monte-carlo --iterations 1000  # combined market-vs-firm report
python run.py --sensitivity labor.g_tools
python run.py --breakeven-sensitivity      # NEW: break-even year across 6 key params
python run.py --crossplot                  # NEW: break-even grid: g_tools × parkinson
python -m pytest tests/ -v                      # 40 tests
```

## Firm model backlog fix (this update)
The previous firm model had a permanent static backlog boost:
  backlog_boost = min(0.40, backlog_months / 30.0)  ← never changed

Now replaced by FirmBacklogStock (firm_model/core/firm_backlog.py):
  - Backlog depletes as engineers clear it (completion_rate × productivity)
  - Refills via firm-specific Parkinson coefficient (industry default)
  - demand_factor fades from 1.0 → 0.0 as backlog approaches equilibrium
  - Industry Parkinson: consumer_tech=0.45, enterprise_saas=0.30,
    fintech=0.20, healthcare/manufacturing=0.15, government=0.10

New FirmProfile field (optional):
  firm_parkinson_override: float = None   # overrides industry default

## Key design decisions

1. Cognitive tools change the COGNITIVE CHARACTER of engineering work, not just speed.
   alpha_cognitive applies to architecture, debugging, requirements — not just coding.
   It is separate from alpha_routine and has its own (slower) maturation curve.

2. Junior engineers benefit LESS from cognitive tools (cognitive_leverage = 0.70).
   Cognitive assistance requires knowing what question to ask, what to specify.
   Juniors lack the domain expertise to effectively direct cognitive AI.
   This is NOT true for routine tools (Copilot-style) where juniors benefit equally.

3. Setting all cognitive params to 0 exactly reproduces v4 behavior.
   Use scenario `cognitive_off` to verify.

4. The cognitive_scope_max = 0.30 default is conservative.
   It means AI never assists more than 30% of cognitive work.
   The optimistic scenario uses 0.50.

## Parameters with NO empirical basis (must be varied in sensitivity analysis)
alpha_cognitive, f_cognitive, cognitive_scope_max, cognitive_growth_rate,
cognitive_maturation_years, parkinson_coefficient, agentic_expansion_rate,
g_tools, f_verify, underserved_fraction, induced_market_size,
annual_cost_reduction_rate, phi

## Parameters with strong empirical grounding
tech_debt_initial_pct: 0.40 (McKinsey 2023, SO 2024 N=65,437)
alpha_experienced: -0.19 (METR RCT, Becker et al. 2025)
ai_debt_premium: 0.35 (CMU SEI 2024)
market baseline growth: 8%/yr (BLS Nov 2025)

## New V5 sensitivity scenarios
fast_tools, slow_tools:       g_tools = 0.35 vs 0.10
low_parkinson, high_parkinson: parkinson = 0.10 vs 0.45
fast_maturation, slow_maturation: alpha maturation in 3yr vs 8yr

## New sensitivity commands
python run.py --breakeven-sensitivity  # 6 parameters × 5-6 values each
python run.py --crossplot              # g_tools × parkinson cross-table

## New V5 cognitive scenarios
cognitive_off:          cognitive disabled; reproduces v4 base exactly
cognitive_conservative: 20% scope max, slow growth (0.10/yr)
cognitive_optimistic:   50% scope max, faster growth (0.25/yr)

## Updated base parameters (v5 revised)
  simulation_years: 5         (horizon; results reported through year 5)
  parkinson_coefficient: 0.25  (was 0.40; lower = weaker Parkinson = sooner break-even)
  alpha_maturation_years: 5.0  (new param; controls METR drag → routine gain transition)
  Result: peak employment at year 4, break-even at year 5

## Key V5 insight
With cognitive tools, the employment outcome becomes MORE EXTREME in both directions:
  - If cognitive leverage drives demand expansion: substantially more engineers
  - If cognitive productivity dominates and demand doesn't expand: substantially fewer
The model shows the break-even year arriving earlier when cognitive tools are more capable.
Over the 5-year horizon:
Base scenario: peaks year 4, starts declining year 5.
Cognitive_optimistic: peaks year 3, starts declining year 4.
