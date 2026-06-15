# Monte Carlo Parameter Ranges — Agentic Coding Labor Model v5

For every variable varied in the Monte Carlo analysis, this table lists both:

- **Hard min / Hard max** — the variable's absolute permissible domain (the model
  breaks or becomes meaningless outside this range), from `docs/variable_documentation.md`.
- **MC low / MC high** — the uniform sampling band actually used in the Monte Carlo
  (documented as the 10th–90th percentile of plausible values). All continuous
  parameters are drawn **uniformly** over `[MC low, MC high]` — uniform because there is
  no basis for assigning probabilities within the plausible range; it represents
  ignorance, not a belief about likelihood.

The **Description** column is a plain-language summary of what each variable means.

> **To change a range for a run, edit `config/monte_carlo_ranges.yaml`** — that file
> holds the same variables and is loaded by every Monte Carlo run. This document is the
> human-readable companion; the YAML is the editable source. If the YAML is missing, the
> model falls back to the built-in defaults in `market_model/core/monte_carlo.py`.

Source of truth: `config/monte_carlo_ranges.yaml` (loaded via `load_mc_ranges`) for the
MC bands, with built-in defaults in `market_model/core/monte_carlo.py`;
`docs/variable_documentation.md` for hard limits.

---

## Market model — `MARKET_MC_PARAMS`

Grouped by the empirical-confidence tier (wider band = less empirical grounding).

### NONE confidence — no empirical basis
| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `labor.g_tools` | How fast agentic coding tools improve each year (the single most impactful uncertain parameter) | 0.00 | 0.80 | 0.08 | 0.45 |
| `demand.parkinson_coefficient` | Share of freed-up capacity that becomes new work rather than headcount savings | 0.00 | 0.70 | 0.05 | 0.50 |
| `context.annual_cost_reduction_rate` | How fast the cost of producing software falls each year | 0.00 | 0.50 | 0.04 | 0.25 |
| `labor.f_verify` | Share of the automation benefit consumed by reviewing AI-generated output | 0.00 | 0.70 | 0.08 | 0.50 |
| `demand.underserved_fraction` | Size of untapped markets (vs. today's market) that cheaper software could unlock | 0.00 | 1.00 | 0.00 | 0.55 |
| `demand.underserved_threshold` | Cost drop required before those underserved markets start adopting software | 0.05 | 0.80 | 0.15 | 0.65 |
| `demand.induced_market_size` | Brand-new software categories AI creates, as a share of today's market | 0.00 | 1.00 | 0.00 | 0.45 |
| `demand.max_cumulative_expansion` | Ceiling on how much cheaper prices can grow demand (Baumol constraint) | 0.05 | 2.00 | 0.20 | 1.00 |
| `production.phi` | Returns to adding engineers; below 1 means coordination overhead (Brooks' Law) | 0.50 | 1.00 | 0.70 | 0.97 |
| `demand.agentic_expansion_rate` | Rate at which newly-feasible projects enter the backlog because tools make them viable | 0.00 | 0.40 | 0.02 | 0.25 |

### Cognitive — all NONE confidence
| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `cognitive.alpha_cognitive` | Productivity gain on cognitive work (architecture, debugging, requirements) when AI-assisted | 0.00 | 0.50 | 0.00 | 0.30 |
| `cognitive.cognitive_scope_max` | The most cognitive work that could ever become AI-assisted | 0.00 | 0.80 | 0.00 | 0.55 |
| `cognitive.cognitive_growth_rate` | How fast cognitive AI assistance grows toward its ceiling each year | 0.00 | 0.60 | 0.05 | 0.35 |
| `cognitive.cognitive_maturation_years` | Years for cognitive AI assistance to fully mature | 2.0 | 20.0 | 4.0 | 14.0 |

### LOW confidence
| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `labor.alpha_maturation_years` | Years for the early productivity drag to give way to routine gains | 1.0 | 15.0 | 2.0 | 8.0 |
| `adoption.q` | Word-of-mouth / imitation speed of tool adoption (Bass diffusion) | 0.05 | 0.80 | 0.20 | 0.55 |
| `adoption.initial_adoption` | Share of engineers already using mature agentic tools at the start | 0.00 | 0.60 | 0.08 | 0.35 |
| `adoption.max_adoption` | Long-run ceiling on tool adoption | 0.40 | 1.00 | 0.70 | 0.95 |
| `demand.backlog_initial_months` | Months of unfinished work in the backlog at the start | 0.5 | 24.0 | 3.0 | 12.0 |

### MEDIUM confidence — empirically grounded, tighter bands
| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `labor.alpha_experienced` | Early productivity effect for experienced devs (negative = slowdown, per METR) | −0.60 | +0.30 | −0.40 | +0.05 |
| `labor.alpha_routine` | Long-run productivity gain on routine tasks (coding, testing, docs) | −0.10 | +0.70 | +0.05 | +0.45 |
| `labor.f_auto` | Fraction of engineering tasks that are automatable | 0.10 | 0.75 | 0.20 | 0.55 |
| `demand.tech_debt_initial_pct` | Share of engineering capacity spent maintaining technical debt today | 5.0 | 80.0 | 25.0 | 58.0 |
| `demand.ai_debt_premium` | Extra technical debt AI-generated code adds per line | 0.00 | 1.00 | 0.10 | 0.65 |

### Consumer capture rates by segment (LOW–MEDIUM)
Hard bounds are `0.00–1.00` for every segment (0.00 = firms keep all savings; 1.00 = all
savings passed to customers).
| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `market.consumer_capture_rate.consumer` | Share of cost savings passed to customers in the consumer segment | 0.00 | 1.00 | 0.35 | 0.90 |
| `market.consumer_capture_rate.smb` | Share of cost savings passed to customers in the small-business segment | 0.00 | 1.00 | 0.25 | 0.80 |
| `market.consumer_capture_rate.enterprise` | Share of cost savings passed to customers in the enterprise segment | 0.00 | 1.00 | 0.10 | 0.60 |
| `market.consumer_capture_rate.regulated` | Share of cost savings passed to customers in the regulated-industry segment | 0.00 | 1.00 | 0.05 | 0.45 |

---

## Firm model — `FIRM_MC_PARAMS` (continuous)

| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `junior_fraction` | Share of the firm's engineers who are junior | 0.05 | 0.70 | 0.20 | 0.55 |
| `senior_fraction` | Share of the firm's engineers who are senior / architect level | 0.05 | 0.50 | 0.12 | 0.35 |
| `revenue_growth_rate` | The firm's current annual revenue growth | −0.20 | 2.00 | 0.02 | 0.35 |
| `long_run_growth_rate` | Steady-state growth the firm's revenue decays toward | −0.20 † | 2.00 † | 0.03 | 0.10 |
| `current_market_penetration` | Share of the firm's total addressable market already captured | 0.001 | 0.90 | 0.02 | 0.50 |
| `build_buy_ratio` | Share of software the firm builds in-house vs. buys (display-only) | 0.00 ‡ | 1.00 ‡ | 0.30 | 0.98 |
| `backlog_months` | Months of unfinished work in the firm's backlog at the start | 0.0 | 36.0 | 2.0 | 18.0 |
| `technical_debt_pct` | Share of the firm's capacity spent maintaining technical debt | 0.0 | 80.0 | 15.0 | 60.0 |
| `agentic_adoption_rate` | Share of the firm's engineers using mature agentic tools | 0.00 | 1.00 | 0.05 | 0.70 |

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

| Variable | Description | Possible values (probability) |
|---|---|---|
| `industry` | The firm's industry sector (sets fork biases and the default firm-Parkinson coefficient) | consumer_tech (0.15), enterprise_saas (0.25), fintech (0.15), healthcare (0.10), manufacturing (0.15), government (0.10), general (0.10) |
| `competitive_intensity` | How competitive the firm's market is | low (0.30), medium (0.45), high (0.25) |
| `capital_efficiency_pressure` | How much pressure the firm is under to cut costs | low (0.25), medium (0.50), high (0.25) |
| `adoption_maturity` | How far along the firm is in adopting agentic tools | early (0.45), developing (0.40), mature (0.15) |
| `will_pass_savings_to_customers` | Whether the firm passes cost savings on to customers | True (0.35), False (0.65) |
| `software_is_core_product` | Whether software is the firm's core product | True (0.55), False (0.45) |
| `has_legacy_modernization` | Whether the firm has a legacy-modernization effort underway | True (0.20), False (0.80) |

### Related: firm-level Parkinson coefficient
The firm-level `firm_parkinson_override` (distinct from the market-level
`demand.parkinson_coefficient`) controls how fast the firm's backlog refills after being
cleared. It has **hard bounds 0.00–0.80** and an **MC band of 0.05–0.60** for a specific
firm. When not overridden, it takes an industry default:

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
