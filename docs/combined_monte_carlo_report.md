# Combined Monte Carlo Report — Market vs. Firm

- **Generated:** 2026-06-15 15:11:06
- **Iterations:** 1,000 each (market + firm)
- **Simulation horizon:** 5 years
- **Firm profile:** Generic Firm (population draw)
- **Base parameters:** `config/market_params.yaml` · **Seed:** 42

> **How to read this.** These are distributions over model outputs given parameter uncertainty — **not** probability forecasts of the future. A wide range reflects how little we know about the inputs, not random chance. Employment figures are an index relative to today: `1.0` = today's level, `1.5` = 50% more, `0.7` = 30% fewer.

Both models are run at the same settings and seed, so they are directly comparable. The **market** model tracks sector-wide employment; the **firm** model tracks one firm's headcount while varying both market parameters *and* the firm's own characteristics.

## 1. Headline distribution (index vs. today)

| Metric | Market P50 | Firm P50 |
|---|---|---|
| Peak index | 1.141 | 1.092 |
| Final index (year 5) | **1.131** | **1.086** |
| P10–P90 final range | 0.761 – 1.535 | 0.964 – 1.263 |
| Never declines | 52.4% | 61.4% |

The median market grows to 1.131×; the median firm grows to 1.086×. The firm distribution is typically **tighter** — its backlog and adoption ramp damp the extremes the market-wide elasticity scenarios produce.

## 2. Direction of outcomes

**Primary split** — mutually exclusive, sums to 100%:

| Direction | Market | Firm |
|---|---|---|
| More engineers than today (>1.0×) | 66.4% | 80.6% |
| Fewer engineers than today (<1.0×) | 33.6% | 19.4% |

**Severity bands** — cumulative tails *nested within* the rows above, so they do **not** add to 100% (e.g. >1.1× is a subset of >1.0×):

| Band | Market | Firm |
|---|---|---|
| Clear expansion | 53.2% (>1.1×) | 7.0% (>1.3×) |
| Clear contraction | 20.9% (<0.9×) | 0.6% (<0.85×) |
| Severe contraction | 7.4% (<0.7×) | — |

*(Severity thresholds differ between the two models — read the bands, not just the percentages.)* Both lean toward growth; the firm leans more strongly and rarely severely contracts.

## 3. Market only — the demand-vs-productivity race

| Quantity | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Demand growth (%/yr) | 7.2 | 10.0 | 13.8 | 17.2 | 20.0 |
| Productivity growth (%/yr) | 5.9 | 9.2 | 13.0 | 17.1 | 21.6 |
| Margin (Demand − Productivity, %/yr) | -7.8 | -4.1 | +0.6 | +5.0 | +9.0 |

- Jevons paradox holds (demand outruns productivity) in **54.1%** of runs.

Top drivers of final market employment (Pearson r):

| Parameter | Correlation | Higher values → |
|---|---|---|
| `labor.g_tools` | -0.564 | fewer engineers |
| `context.annual_cost_reduction_rate` | +0.480 | more engineers |
| `demand.underserved_threshold` | -0.342 | fewer engineers |
| `demand.agentic_expansion_rate` | +0.207 | more engineers |
| `demand.backlog_initial_months` | +0.178 | more engineers |

## 4. Firm only — tier split & management response

| Metric | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Final senior index | 1.212 | 1.276 | 1.364 | 1.478 | 1.614 |
| Final junior index | 0.806 | 0.861 | 0.921 | 0.993 | 1.075 |
| Senior − Junior gap | 0.331 | 0.371 | 0.440 | 0.529 | 0.604 |

- Senior beats junior in **100.0%** of runs.

Management fork distribution:

| Fork | Share of runs |
|---|---|
| HARVEST | 25.7% |
| REINVEST | 36.6% |
| EXPAND | 21.2% |
| IMPROVE | 16.5% |

## 5. Consistency cross-check

The firm run carries a **market-index reference of P50 = 1.130**, versus the standalone market report's final P50 of **1.131**. Close agreement confirms both runs draw from the same underlying market model (same seed); the firm report layers firm-specific dynamics on top.

## 6. Bottom line

- **Same direction, different shape.** Both lean growth-ward (market 1.131×, firm 1.086×), but the market is a wide two-tailed distribution while the firm is narrow and mostly positive.
- **The market hides the tier story; the firm exposes it.** Aggregate firm headcount barely moves, but seniors (P50 1.364×) grow while juniors (P50 0.921×) shrink — in 100% of runs.
- **Most common firm response:** REINVEST (37% of runs).
- Treat the spread as a map of our ignorance, not a probability of the future.

## Appendix — Parameter ranges used in this run

Source: `config/monte_carlo_ranges.yaml`

These are the exact sampling bands drawn from for this run. **MC low / MC high** is the uniform band each variable was drawn from; **Hard min / Hard max** are the absolute bounds (informational).

### Market model

| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `labor.g_tools` | How fast agentic coding tools improve each year (the single most impactful uncertain parameter) | 0.0 | 0.8 | 0.08 | 0.45 |
| `demand.parkinson_coefficient` | Share of freed-up capacity that becomes new work rather than headcount savings | 0.0 | 0.7 | 0.05 | 0.5 |
| `context.annual_cost_reduction_rate` | How fast the cost of producing software falls each year | 0.0 | 0.5 | 0.04 | 0.25 |
| `labor.f_verify` | Share of the automation benefit consumed by reviewing AI-generated output | 0.0 | 0.7 | 0.08 | 0.5 |
| `demand.underserved_fraction` | Size of untapped markets (vs. today's market) that cheaper software could unlock | 0.0 | 1.0 | 0.0 | 0.55 |
| `demand.underserved_threshold` | Cost drop required before those underserved markets start adopting software | 0.05 | 0.8 | 0.15 | 0.65 |
| `demand.induced_market_size` | Brand-new software categories AI creates, as a share of today's market | 0.0 | 1.0 | 0.0 | 0.45 |
| `demand.max_cumulative_expansion` | Ceiling on how much cheaper prices can grow demand (Baumol constraint) | 0.05 | 2.0 | 0.2 | 1.0 |
| `production.phi` | Returns to adding engineers; below 1 means coordination overhead (Brooks' Law) | 0.5 | 1.0 | 0.7 | 0.97 |
| `demand.agentic_expansion_rate` | Rate at which newly-feasible projects enter the backlog because tools make them viable | 0.0 | 0.4 | 0.02 | 0.25 |
| `cognitive.alpha_cognitive` | Productivity gain on cognitive work (architecture, debugging, requirements) when AI-assisted | 0.0 | 0.5 | 0.0 | 0.3 |
| `cognitive.cognitive_scope_max` | The most cognitive work that could ever become AI-assisted | 0.0 | 0.8 | 0.0 | 0.55 |
| `cognitive.cognitive_growth_rate` | How fast cognitive AI assistance grows toward its ceiling each year | 0.0 | 0.6 | 0.05 | 0.35 |
| `cognitive.cognitive_maturation_years` | Years for cognitive AI assistance to fully mature | 2.0 | 20.0 | 4.0 | 14.0 |
| `labor.alpha_maturation_years` | Years for the early productivity drag to give way to routine gains | 1.0 | 15.0 | 2.0 | 8.0 |
| `adoption.q` | Word-of-mouth / imitation speed of tool adoption (Bass diffusion) | 0.05 | 0.8 | 0.2 | 0.55 |
| `adoption.initial_adoption` | Share of engineers already using mature agentic tools at the start | 0.0 | 0.6 | 0.08 | 0.35 |
| `adoption.max_adoption` | Long-run ceiling on tool adoption | 0.4 | 1.0 | 0.7 | 0.95 |
| `demand.backlog_initial_months` | Months of unfinished work in the backlog at the start | 0.5 | 24.0 | 3.0 | 12.0 |
| `labor.alpha_experienced` | Early productivity effect for experienced devs (negative = slowdown, per METR) | -0.6 | 0.3 | -0.4 | 0.05 |
| `labor.alpha_routine` | Long-run productivity gain on routine tasks (coding, testing, docs) | -0.1 | 0.7 | 0.05 | 0.45 |
| `labor.f_auto` | Fraction of engineering tasks that are automatable | 0.1 | 0.75 | 0.2 | 0.55 |
| `demand.tech_debt_initial_pct` | Share of engineering capacity spent maintaining technical debt today | 5.0 | 80.0 | 25.0 | 58.0 |
| `demand.ai_debt_premium` | Extra technical debt AI-generated code adds per line | 0.0 | 1.0 | 0.1 | 0.65 |
| `market.consumer_capture_rate.consumer` | Share of cost savings passed to customers in the consumer segment | 0.0 | 1.0 | 0.35 | 0.9 |
| `market.consumer_capture_rate.smb` | Share of cost savings passed to customers in the small-business segment | 0.0 | 1.0 | 0.25 | 0.8 |
| `market.consumer_capture_rate.enterprise` | Share of cost savings passed to customers in the enterprise segment | 0.0 | 1.0 | 0.1 | 0.6 |
| `market.consumer_capture_rate.regulated` | Share of cost savings passed to customers in the regulated-industry segment | 0.0 | 1.0 | 0.05 | 0.45 |

### Firm model (continuous)

| Variable | Description | Hard min | Hard max | MC low | MC high |
|---|---|---|---|---|---|
| `junior_fraction` | Share of the firm's engineers who are junior | 0.05 | 0.7 | 0.2 | 0.55 |
| `senior_fraction` | Share of the firm's engineers who are senior / architect level | 0.05 | 0.5 | 0.12 | 0.35 |
| `revenue_growth_rate` | The firm's current annual revenue growth | -0.2 | 2.0 | 0.02 | 0.35 |
| `long_run_growth_rate` | Steady-state growth the firm's revenue decays toward (not clamped in code) | -0.2 | 2.0 | 0.03 | 0.1 |
| `current_market_penetration` | Share of the firm's total addressable market already captured | 0.001 | 0.9 | 0.02 | 0.5 |
| `build_buy_ratio` | Share of software the firm builds in-house vs. buys (display-only in the model) | 0.0 | 1.0 | 0.3 | 0.98 |
| `backlog_months` | Months of unfinished work in the firm's backlog at the start | 0.0 | 36.0 | 2.0 | 18.0 |
| `technical_debt_pct` | Share of the firm's capacity spent maintaining technical debt | 0.0 | 80.0 | 15.0 | 60.0 |
| `agentic_adoption_rate` | Share of the firm's engineers using mature agentic tools | 0.0 | 1.0 | 0.05 | 0.7 |

### Firm model (categorical)

| Variable | Description | Categories (probability) |
|---|---|---|
| `industry` | The firm's industry sector (sets fork biases and the default firm-Parkinson coefficient) | consumer_tech (0.15), enterprise_saas (0.25), fintech (0.15), healthcare (0.1), manufacturing (0.15), government (0.1), general (0.1) |
| `competitive_intensity` | How competitive the firm's market is | low (0.3), medium (0.45), high (0.25) |
| `capital_efficiency_pressure` | How much pressure the firm is under to cut costs | low (0.25), medium (0.5), high (0.25) |
| `adoption_maturity` | How far along the firm is in adopting agentic tools | early (0.45), developing (0.4), mature (0.15) |
| `will_pass_savings_to_customers` | Whether the firm passes cost savings on to customers | True (0.35), False (0.65) |
| `software_is_core_product` | Whether software is the firm's core product | True (0.55), False (0.45) |
| `has_legacy_modernization` | Whether the firm has a legacy-modernization effort underway | True (0.2), False (0.8) |
