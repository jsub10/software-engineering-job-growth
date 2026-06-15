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
Peak employment:   1.150× baseline  (year 8)
Break-even year:   year 9            (first year employment starts declining)
Final employment:  1.143× baseline  (year 10)
```

Read as: under base assumptions, employment rises 15% above baseline by year 8,
then starts declining. By year 10, still 14% above baseline. The trajectory matters
more than any single number.

## V5 vs V4 Comparison

| Scenario              | Peak | Peak Yr | Break-Even | Final |
|---|---|---|---|---|
| cognitive_off (= v4)  | 1.174 | 10 | never | 1.174 |
| cognitive_conservative | 1.166 | 9 | yr 10 | 1.164 |
| base (v5 default)     | 1.150 | 8 | yr 9  | 1.143 |
| cognitive_optimistic  | 1.116 | 4 | yr 5  | 1.059 |

More cognitive capability → earlier peak → earlier decline. The break-even year
is the key indicator to watch in practice.

## Tier Effects

The widening skill pyramid is V5's most important structural prediction:

| Scenario | Junior | Mid | Senior | Architect (relative) |
|---|---|---|---|---|
| cognitive_off | 0.962 | 1.127 | 1.432 | — |
| base (v5) | 0.872 | 1.123 | 1.524 | higher |
| cognitive_optimistic | 0.749 | 1.063 | 1.529 | highest |

Junior employment falls as cognitive tools become more capable — not because
junior engineers are displaced by routine automation (that's already in v4),
but because cognitive tools require expertise to direct, and juniors lack that
expertise. The skill premium for senior engineers grows with cognitive tool capability.

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
    └── test_v4.py                    ← 40 tests (31 v4 + 9 cognitive)
```

## Quickstart

```bash
pip install -r requirements.txt
python run.py                                     # base with v5 cognitive
python run.py --scenarios all                     # all 11 scenarios
python run.py --scenario cognitive_optimistic     # aggressive cognitive
python run.py --scenario cognitive_off            # v4 behavior exactly
python run.py --firm-compare                      # all firm profiles
python run.py --monte-carlo --iterations 1000
python -m pytest tests/ -v                        # 40 tests
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
