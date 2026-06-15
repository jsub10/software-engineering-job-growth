# Agentic Coding Labor Model v5

## The New Question V5 Answers

V4 modeled agentic coding as automating a fixed fraction of engineering *tasks*
(routine code, testing, documentation). V5 adds a fundamentally different mechanism:
cognitive capability replication.

Agentic tools are beginning to assist with four types of cognitive work that
previous versions treated as permanently human:

  - Specification and decomposition: breaking problems into solvable pieces
  - Context synthesis: understanding large codebases before changing them
  - Debugging hypothesis generation: reasoning about what could be wrong
  - Requirements formalization: turning vague needs into precise specifications

This changes the model's predictions in a specific way: productivity grows faster
and to a higher ceiling, but the *distribution* of that productivity gain across
the engineering skill pyramid becomes more skewed. Senior engineers who already
know what architectural question to ask get dramatically more leverage from cognitive
AI. Junior engineers — who don't yet have the domain expertise to direct cognitive AI
effectively — see less benefit from cognitive tools than from routine automation tools.

## Primary Output: Three Numbers

```
Peak employment:   1.112× baseline  (year 4)
Break-even year:   year 5            (first year employment starts declining)
Final employment:  1.106× baseline  (year 5)
```

Read as: under base assumptions, employment rises 11% above baseline by year 4,
then starts declining. By year 5 (the end of the modeled horizon), still 11% above
baseline. The trajectory matters more than any single number.

## V5 vs V4 Comparison

Over the 5-year horizon (`context.simulation_years: 5`):

| Scenario              | Peak | Peak Yr | Break-Even | Final |
|---|---|---|---|---|
| cognitive_off (= v4)  | 1.114 | 4 | yr 5 | 1.111 |
| cognitive_conservative | 1.113 | 4 | yr 5 | 1.110 |
| base (v5 default)     | 1.112 | 4 | yr 5 | 1.106 |
| cognitive_optimistic  | 1.106 | 3 | yr 4 | 1.090 |

More cognitive capability → earlier peak → earlier decline. The break-even year
is the key indicator to watch in practice. Within a 5-year window the scenarios
compress (all peak around year 4); the divergence between them widens over longer
horizons.

## Tier Effects

The widening skill pyramid is V5's most important structural prediction:

Employment index by tier at year 5:

| Scenario | Junior | Mid | Senior | Architect (relative) |
|---|---|---|---|---|
| cognitive_off | 0.911 | 1.066 | 1.285 | — |
| base (v5) | 0.864 | 1.079 | 1.361 | higher |
| cognitive_optimistic | 0.798 | 1.083 | 1.441 | highest |

Junior employment falls as cognitive tools become more capable — not because
junior engineers are displaced by routine automation (that's already in v4),
but because cognitive tools require expertise to direct, and juniors lack that
expertise. The skill premium for senior engineers grows with cognitive tool capability.

## Documentation

- [docs/monte_carlo_ranges.md](docs/monte_carlo_ranges.md) — Monte Carlo parameter ranges: hard limits vs. sampling bands for every varied variable
- [docs/monte_carlo_results.md](docs/monte_carlo_results.md) — Monte Carlo results report (1,000 iterations)
- [docs/market_vs_firm_comparison.md](docs/market_vs_firm_comparison.md) — Market vs. firm Monte Carlo, side by side
- [docs/variable_documentation.md](docs/variable_documentation.md) — Complete variable reference: base values, hard limits, MC ranges, empirical confidence
- [docs/v5_cognitive_additions.md](docs/v5_cognitive_additions.md) — Why and how the cognitive components work
- [docs/model_explanation_detailed.md](docs/model_explanation_detailed.md) — Detailed model walkthrough
- [docs/model_explanation_simple.md](docs/model_explanation_simple.md) — Plain-language overview

## Architecture

```
agentic-labor-model-v5/
├── README.md
├── CLAUDE.md                         ← Claude Code instructions
├── requirements.txt
├── run.py
├── docs/
│   ├── v5_cognitive_additions.md     ← Why and how cognitive components work
│   ├── model_explanation_detailed.md
│   └── model_explanation_simple.md
├── config/
│   ├── market_params.yaml            ← Now includes [cognitive] section
│   └── scenarios.yaml                ← Now includes cognitive scenarios
├── market_model/
│   ├── core/
│   │   ├── breakeven.py              ← Three-component alpha + cognitive scope
│   │   ├── demand_stocks.py
│   │   ├── demand_saturation.py
│   │   ├── model.py                  ← Cognitive leverage in tier adjustments
│   │   ├── exogenous.py
│   │   ├── scenario_runner.py
│   │   └── uncertainty.py
│   └── diffusion/
│       └── bass.py
├── firm_model/
│   ├── core/
│   │   └── firm_model.py             ← Cognitive leverage in _tier_adjustments
│   └── profiles/
│       ├── enterprise_saas.yaml
│       ├── regulated_bank.yaml
│       ├── consumer_startup.yaml
│       └── manufacturing_it.yaml
└── tests/
    └── test_v4.py                    ← 48 tests (v4 core + cognitive + firm backlog)
```

## Quickstart

```bash
pip install -r requirements.txt
python run.py                                     # base with v5 cognitive
python run.py --scenarios all                     # all 16 scenarios
python run.py --scenario cognitive_optimistic     # aggressive cognitive
python run.py --scenario cognitive_off            # v4 behavior exactly
python run.py --firm-compare                      # all firm profiles
python run.py --monte-carlo --iterations 1000
python -m pytest tests/ -v                        # 48 tests
```

## Empirical Confidence

The cognitive additions are all NO EMPIRICAL BASIS:

| Parameter | Default | Confidence |
|---|---|---|
| alpha_cognitive | 0.15 | NONE — no studies |
| f_cognitive | 0.35 | NONE — estimated |
| cognitive_scope_max | 0.30 | NONE — assumption |
| cognitive_growth_rate | 0.15 | NONE — assumption |
| cognitive_maturation_years | 8.0 | NONE — assumption |

Set `cognitive_scope_max: 0` to reproduce v4 exactly and test sensitivity
to the cognitive assumptions.

## What to Watch in Practice

The model suggests three empirical signals that will reveal whether the cognitive
mechanism is materializing:

1. **Senior/junior wage premium.** If cognitive tools are widening the skill
   pyramid, the premium for senior engineers should be rising. Watch L4+ vs L3
   compensation ratios at major tech firms.

2. **Requirements and architecture tooling adoption.** The first sign of cognitive
   scope expanding beyond coding is adoption of AI tools for specification, design
   docs, and architectural review — not just code generation.

3. **Junior engineer utilization rates.** If junior engineers are spending more
   time directing AI and less time coding, their output per engineer-hour should
   rise faster than v4 predicts. If they're spending time correcting AI output,
   the METR slowdown finding may generalize to them too.
