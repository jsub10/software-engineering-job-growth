# Market vs. Firm Monte Carlo — Side-by-Side Comparison

**Run date:** 2026-06-15 · **Iterations:** 1,000 each · **Horizon:** 5 years · **Seed:** 42
**Firm profile:** Generic Firm (population draw)

> These are distributions over model outputs given parameter uncertainty — **not**
> forecasts. Both models were run at identical settings and seed, so they are directly
> comparable. The **market** model tracks sector-wide employment; the **firm** model
> tracks one firm's headcount while varying *both* market parameters and the firm's own
> characteristics. Index is relative to today (`1.0` = today, `1.5` = +50%, `0.7` = −30%).
>
> This document is a snapshot. To regenerate it for the current config, run:
> `python run.py --combined-monte-carlo --iterations 1000`

---

## 1. Headline distribution (index vs. today, P50)

| Metric | Market | Firm |
|---|---|---|
| Peak index | 1.141 | 1.092 |
| Final index (year 5) | **1.131** | **1.086** |
| P10–P90 final range | 0.761 – 1.535 | 0.964 – 1.263 |
| Never declines | 52.4% | 61.4% |

**The firm spread is much tighter** (0.96–1.26 vs. 0.76–1.54). The firm's backlog and
adoption ramp cushion near-term headcount, so it avoids both the deep-contraction and
high-expansion tails the market aggregate shows.

## 2. Direction of outcomes

| Outcome | Market | Firm |
|---|---|---|
| Ends **above** baseline (>1.0×) | 66.4% | **80.6%** |
| Clear expansion | 53.2% (>1.1×) | 7.0% (>1.3×) |
| Contraction | 20.9% (<0.9×) / 7.4% (<0.7×) | 0.6% (<0.85×) |

*(Verdict thresholds differ between the two models — market uses 1.1×/0.9×/0.7×, firm
uses 1.3×/0.85× — so read the bands, not just the percentages.)* Both lean toward growth;
**the firm leans more strongly** and almost never severely contracts.

## 3. Market only — the demand-vs-productivity race

| Quantity | P50 |
|---|---|
| Demand growth | 13.8%/yr |
| Productivity growth | 13.0%/yr |
| Margin (Demand − Productivity) | +0.6%/yr (Jevons holds in 54.1% of runs) |

Top drivers of final market employment: `labor.g_tools` (−0.56),
`context.annual_cost_reduction_rate` (+0.48), `demand.underserved_threshold` (−0.34),
`demand.agentic_expansion_rate` (+0.21).

## 4. Firm only — tier split & management response

| Tier (P50) | Index |
|---|---|
| Senior | 1.364 |
| Junior | 0.921 |
| Senior − Junior gap | +0.440 (senior > junior in **100%** of runs) |

Management fork: REINVEST 36.6% · HARVEST 25.7% · EXPAND 21.2% · IMPROVE 16.5%.

## 5. Consistency cross-check ✓

The firm report carries a **"final market index (reference)" of P50 = 1.130** — essentially
identical to the market report's final **1.131**. That confirms both runs draw from the
same underlying market model (seed 42); the firm report layers firm-specific dynamics on
top of that same market.

## 6. Bottom line

- **Same direction, different shape.** Both lean growth-ward, but the market is a wide,
  two-tailed distribution (a real chance of contraction) while the firm is a narrow,
  mostly-positive one.
- **The market hides the tier story; the firm exposes it.** Aggregate firm headcount
  barely moves (~1.09×), but underneath, seniors grow ~+36% while juniors shrink ~−8% —
  unanimously, in every run. The skill-pyramid widening is the firm report's signature
  finding and isn't visible in the market headline.
- **The firm's stability is structural, not luck** — its backlog + adoption ramp damp the
  extremes that the market-wide elasticity scenarios produce.

---

*Generated from the combined Monte Carlo report (`output/mc_report.py`,
`write_combined_mc_report`). The live, timestamped version of this comparison —
including the full parameter-range appendix — is produced by
`python run.py --combined-monte-carlo`.*
