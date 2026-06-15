# Monte Carlo Results — Agentic Coding Labor Model v5

**Run date:** 2026-06-15
**Iterations:** 1,000
**Command:** `python run.py --monte-carlo --iterations 1000`

---

## How to read this

This Monte Carlo varies **all uncertain parameters simultaneously**, drawing each
from its plausible range, and runs the full 10-year labor model once per draw. The
spread of outcomes you see below reflects **how little we know about the input
parameters** — it is *not* a probability forecast of the future.

> **Important caveat (from the model itself):** These are distributions over model
> outputs given parameter uncertainty. They are **not** probability forecasts of
> future employment. Wide ranges reflect parameter ignorance, not random chance.

The employment numbers are an **index relative to today**: `1.0` = today's software
engineering employment, `1.5` = 50% more engineers, `0.7` = 30% fewer.

---

## 1. Primary outputs

Percentiles across all 1,000 runs (P50 = median; P10–P90 = the middle 80% of outcomes):

| Metric | P10 | P25 | P50 (median) | P75 | P90 |
|---|---|---|---|---|---|
| **Peak employment index** | 0.968 | 1.015 | **1.164** | 1.488 | 1.841 |
| **Peak year** | 1 | 2 | **5** | 10 | 10 |
| **Break-even year** (when it declines) | 2 | 2 | **4** | 7 | 8 |
| **Final employment (year 10)** | 0.300 | 0.446 | **0.986** | 1.418 | 1.839 |

- **Employment never declines in 26.0% of runs** — in roughly a quarter of scenarios,
  engineering employment grows for the full decade and never turns down.

### What this says
- The **typical (median) path** sees employment climb modestly to a peak of **~1.16×
  today's level around year 5**, then drift back down to **~0.99× by year 10** — i.e.
  roughly flat over the decade, with a hump in the middle.
- But the **range is enormous**: by year 10 the middle-80% band runs from **0.30×
  (a 70% contraction)** all the way to **1.84× (an 84% expansion)**. The model does not
  confidently predict either job loss or job growth — the input uncertainty dominates.

---

## 2. The break-even margin (year 10)

Employment direction is governed by a race between two forces:
**demand growth** (more software wanted) vs. **productivity growth** (each engineer
does more). The difference between them is the **margin**.

| Quantity | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Demand growth (%/yr) | 12.4 | 15.2 | **19.2** | 24.4 | 30.0 |
| Productivity growth (%/yr) | 13.6 | 19.2 | **25.7** | 32.5 | 38.8 |
| **Margin (Demand − Productivity, %/yr)** | −18.0 | −11.9 | **−5.0** | +1.1 | +5.7 |

- **Jevons paradox holds (demand outruns productivity) in only 28.1% of runs.**

### What this says
- In the **median** run, productivity grows **faster** than demand (25.7% vs 19.2%/yr),
  giving a **negative margin of −5.0%/yr** — meaning the same software gets built with
  fewer engineers each year. This is why median employment ends up roughly flat-to-down.
- For employment to keep growing, the **"Jevons" effect** (cheaper software → so much
  more software demanded that net headcount rises) must win. That happens in only about
  **1 in 4** parameter combinations here.

---

## 2a. Year-3 snapshot — demand vs. productivity

The break-even race plays out over time, so the early years look very different
from year 10. Looking specifically at **year 3** (extracted with `year3_analysis.py`,
which replays the identical MC draw — seed 42, same parameter order):

| | Productivity grows **≥** demand | Demand wins (Jevons holds) |
|---|---|---|
| **Year 3** | **30.1%** of runs | 69.9% |
| **Year 10** | ~71.9% of runs | 28.1% |

**At year 3, productivity grows as fast or faster than demand in only 30.1% of runs**
(301 of 1,000 — all strictly faster; exact ties have effectively zero probability with
continuous draws). In the other **69.9%**, demand is still outrunning productivity.

Year-3 growth-rate distribution:

| Quantity | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Demand growth (%/yr) | — | — | **9.7** | — | — |
| Productivity growth (%/yr) | — | — | **7.5** | — | — |
| Margin (Demand − Productivity, %/yr) | −3.4 | −0.6 | **+2.8** | +6.5 | +11.1 |

### What this says — the picture *flips* over the decade
The median year-3 margin is **+2.8%/yr** (demand winning), versus **−5.0%/yr at year 10**
(productivity winning). Early on, demand growth is still high because the backlog hasn't
been depleted, while productivity gains are suppressed (METR drag, plus routine/cognitive
automation not yet matured). By year 10 that reverses: productivity accelerates as tools
mature and demand decays as backlog clears. **Year 3 sits firmly in the "demand still
winning" regime for ~70% of scenarios** — the crossover to productivity-dominance comes
later.

---

## 3. Verdicts — how often does each outcome occur?

Share of the 1,000 runs ending in each state at year 10:

| Outcome at year 10 | Share of runs |
|---|---|
| Final employment **> baseline (1.0×)** — net job growth | **49.3%** |
| Final employment **> 1.1×** — clear expansion | 43.7% |
| Final employment **< 0.9×** — clear contraction | 46.7% |
| Final employment **< 0.7×** — severe contraction | 37.5% |

### What this says
The outcome is **almost a coin flip**: ~49% of scenarios end with more engineers than
today, ~47% with meaningfully fewer. The tails are heavy on both sides — a **clear
expansion (43.7%)** and a **severe contraction below 0.7× (37.5%)** are both very common.
This is the v5 model's headline insight in action: **cognitive tools push the outcome to
extremes in both directions.**

---

## 4. What drives the outcome — parameter influence

Pearson correlation between each drawn parameter and final (year-10) employment.
Sign shows direction; magnitude shows strength.

| Parameter | Correlation | Effect on employment |
|---|---|---|
| `labor.g_tools` (tool capability growth rate) | **−0.598** | ↑ tool power → **fewer** engineers (strongest driver) |
| `demand.agentic_expansion_rate` | +0.301 | ↑ → more engineers |
| `context.annual_cost_reduction_rate` | +0.287 | ↑ → more engineers |
| `demand.backlog_initial_months` | +0.283 | ↑ starting backlog → more engineers |
| `demand.underserved_threshold` | −0.252 | ↑ → fewer engineers |
| `labor.alpha_routine` | −0.229 | ↑ routine automation → fewer engineers |
| `demand.parkinson_coefficient` | +0.207 | ↑ work-expands-to-fill → more engineers |
| `adoption.q` (diffusion speed) | −0.158 | ↑ faster adoption → fewer engineers |

### What this says
- **The single most important lever is `g_tools`** — how fast agentic coding tools grow
  in capability. The faster tools improve, the more strongly employment falls
  (r = −0.60, by far the dominant factor).
- The **counterweights** are demand-side: how much AI *expands* what gets built
  (`agentic_expansion_rate`), how cheap context/compute gets (`annual_cost_reduction_rate`),
  the size of the starting backlog, and how strongly work expands to fill capacity
  (`parkinson_coefficient`). When these run high, employment grows.
- Crucially, **the strongest driver (`g_tools`) has no empirical basis** in the model —
  it's an assumption. So the wide spread above is honest: the outcome hinges most on the
  parameter we know the least about.

---

## 5. Bottom line

1. **No confident prediction either way.** The median decade is roughly flat (peak ~1.16×
   around year 5, ending ~0.99×), but the 80% range spans a 70% contraction to an 84%
   expansion.
2. **It's close to a coin flip** whether there are more or fewer engineers in 10 years
   (49% up vs 47% down), with **fat tails on both ends**.
3. **The deciding factor is how fast tools get more capable** (`g_tools`), partially
   offset by how much AI expands total demand for software.
4. **Treat the spread as a map of our ignorance**, not a probability of the future — the
   biggest driver is also the least empirically grounded parameter.

---

*Generated from `market_model/core/monte_carlo.py`. Reproduce with:*
`python run.py --monte-carlo --iterations 1000`
