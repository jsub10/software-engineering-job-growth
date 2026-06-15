# Monte Carlo Parameter Ranges — Agentic Coding Labor Model v5

For every variable varied in the Monte Carlo analysis, this table lists both:

- **Hard min / Hard max** — the variable's absolute permissible domain (the model
  breaks or becomes meaningless outside this range), from `docs/variable_documentation.md`.
- **MC low / MC high** — the uniform sampling band actually used in the Monte Carlo
  (documented as the 10th–90th percentile of plausible values). All continuous
  parameters are drawn **uniformly** over `[MC low, MC high]` — uniform because there is
  no basis for assigning probabilities within the plausible range; it represents
  ignorance, not a belief about likelihood.

Source of truth: `market_model/core/monte_carlo.py` (`MARKET_MC_PARAMS`, `FIRM_MC_PARAMS`,
`FIRM_CATEGORICAL`) for the MC bands; `docs/variable_documentation.md` for hard limits.

---

## Market model — `MARKET_MC_PARAMS`

Grouped by the empirical-confidence tier (wider band = less empirical grounding).

### NONE confidence — no empirical basis
| Variable | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|
| `labor.g_tools` | 0.00 | 0.80 | 0.08 | 0.45 |
| `demand.parkinson_coefficient` | 0.00 | 0.70 | 0.05 | 0.50 |
| `context.annual_cost_reduction_rate` | 0.00 | 0.50 | 0.04 | 0.25 |
| `labor.f_verify` | 0.00 | 0.70 | 0.08 | 0.50 |
| `demand.underserved_fraction` | 0.00 | 1.00 | 0.00 | 0.55 |
| `demand.underserved_threshold` | 0.05 | 0.80 | 0.15 | 0.65 |
| `demand.induced_market_size` | 0.00 | 1.00 | 0.00 | 0.45 |
| `demand.max_cumulative_expansion` | 0.05 | 2.00 | 0.20 | 1.00 |
| `production.phi` | 0.50 | 1.00 | 0.70 | 0.97 |
| `demand.agentic_expansion_rate` | 0.00 | 0.40 | 0.02 | 0.25 |

### Cognitive — all NONE confidence
| Variable | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|
| `cognitive.alpha_cognitive` | 0.00 | 0.50 | 0.00 | 0.30 |
| `cognitive.cognitive_scope_max` | 0.00 | 0.80 | 0.00 | 0.55 |
| `cognitive.cognitive_growth_rate` | 0.00 | 0.60 | 0.05 | 0.35 |
| `cognitive.cognitive_maturation_years` | 2.0 | 20.0 | 4.0 | 14.0 |

### LOW confidence
| Variable | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|
| `labor.alpha_maturation_years` | 1.0 | 15.0 | 2.0 | 8.0 |
| `adoption.q` | 0.05 | 0.80 | 0.20 | 0.55 |
| `adoption.initial_adoption` | 0.00 | 0.60 | 0.08 | 0.35 |
| `adoption.max_adoption` | 0.40 | 1.00 | 0.70 | 0.95 |
| `demand.backlog_initial_months` | 0.5 | 24.0 | 3.0 | 12.0 |

### MEDIUM confidence — empirically grounded, tighter bands
| Variable | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|
| `labor.alpha_experienced` | −0.60 | +0.30 | −0.40 | +0.05 |
| `labor.alpha_routine` | −0.10 | +0.70 | +0.05 | +0.45 |
| `labor.f_auto` | 0.10 | 0.75 | 0.20 | 0.55 |
| `demand.tech_debt_initial_pct` | 5.0 | 80.0 | 25.0 | 58.0 |
| `demand.ai_debt_premium` | 0.00 | 1.00 | 0.10 | 0.65 |

### Consumer capture rates by segment (LOW–MEDIUM)
Hard bounds are `0.00–1.00` for every segment (0.00 = firms keep all savings; 1.00 = all
savings passed to customers).
| Variable | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|
| `market.consumer_capture_rate.consumer` | 0.00 | 1.00 | 0.35 | 0.90 |
| `market.consumer_capture_rate.smb` | 0.00 | 1.00 | 0.25 | 0.80 |
| `market.consumer_capture_rate.enterprise` | 0.00 | 1.00 | 0.10 | 0.60 |
| `market.consumer_capture_rate.regulated` | 0.00 | 1.00 | 0.05 | 0.45 |

---

## Firm model — `FIRM_MC_PARAMS` (continuous)

| Variable | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|
| `junior_fraction` | 0.05 | 0.70 | 0.20 | 0.55 |
| `senior_fraction` | 0.05 | 0.50 | 0.12 | 0.35 |
| `revenue_growth_rate` | −0.20 | 2.00 | 0.02 | 0.35 |
| `long_run_growth_rate` | −0.20 † | 2.00 † | 0.03 | 0.10 |
| `current_market_penetration` | 0.001 | 0.90 | 0.02 | 0.50 |
| `build_buy_ratio` | 0.00 ‡ | 1.00 ‡ | 0.30 | 0.98 |
| `backlog_months` | 0.0 | 36.0 | 2.0 | 18.0 |
| `technical_debt_pct` | 0.0 | 80.0 | 15.0 | 60.0 |
| `agentic_adoption_rate` | 0.00 | 1.00 | 0.05 | 0.70 |

**† `long_run_growth_rate`** — not separately documented in `variable_documentation.md`
and **not clamped in code**. It is the asymptote that `revenue_growth_rate` decays toward
(`firm_model.py:208`, used as `max(g_lr, g_t)`), i.e. the same quantity as
`revenue_growth_rate`, so its conceptual domain is the same (−0.20 to 2.00). In practice
the shipped profiles span 0.02–0.08.

**‡ `build_buy_ratio`** — not separately documented and **not clamped in code**; it is
currently **display-only** (`firm_model.py:435`) and does not enter any calculation. By
definition it is a fraction (share of software built vs. bought), so its domain is
0.00–1.00. Shipped profiles span 0.45–0.95.

### Anchoring caveat for firm continuous params
When a base firm profile supplies a value for one of these fields, the MC draw is
**anchored**: it samples within **±50% of the half-range around the base value**, then
clips to the hard `[low, high]`. This keeps the firm "type" recognizable while exploring
uncertainty. The MC low/high columns above are the **unanchored** bounds (used when the
profile has no value, e.g. a "Generic" profile). After drawing,
`junior_fraction + senior_fraction` is rescaled down if it exceeds **0.90** (leaving room
for the implicit mid tier).

---

## Firm model — `FIRM_CATEGORICAL` (discrete)

Min/max do not apply — these are drawn from discrete probability distributions, and
**only when the profile name starts with "Generic"**; otherwise the profile's own values
are kept. The probabilities are:

| Variable | Possible values (probability) |
|---|---|
| `industry` | consumer_tech (0.15), enterprise_saas (0.25), fintech (0.15), healthcare (0.10), manufacturing (0.15), government (0.10), general (0.10) |
| `competitive_intensity` | low (0.30), medium (0.45), high (0.25) |
| `capital_efficiency_pressure` | low (0.25), medium (0.50), high (0.25) |
| `adoption_maturity` | early (0.45), developing (0.40), mature (0.15) |
| `will_pass_savings_to_customers` | True (0.35), False (0.65) |
| `software_is_core_product` | True (0.55), False (0.45) |
| `has_legacy_modernization` | True (0.20), False (0.80) |

### Related: firm-level Parkinson coefficient
The firm-level `firm_parkinson_override` (distinct from the market-level
`demand.parkinson_coefficient`) has **hard bounds 0.00–0.80** and an **MC band of
0.05–0.60** for a specific firm. When not overridden, it takes an industry default:

| Industry | Default |
|---|---|
| consumer_tech | 0.45 |
| enterprise_saas | 0.30 |
| fintech | 0.20 |
| healthcare | 0.15 |
| manufacturing | 0.15 |
| government | 0.10 |

---

*Generated from `market_model/core/monte_carlo.py` and `docs/variable_documentation.md`.*
