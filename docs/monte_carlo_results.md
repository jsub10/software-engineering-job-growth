# Monte Carlo Results — Agentic Coding Labor Model v5

**Run date:** 2026-06-15
**Iterations:** 1,000
**Simulation horizon:** 5 years
**Command:** `python run.py --monte-carlo --iterations 1000`

---

## How to read this

This Monte Carlo varies **all uncertain parameters simultaneously**, drawing each
from its plausible range, and runs the full 5-year labor model once per draw. The
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
| **Peak employment index** | 0.968 | 1.014 | **1.141** | 1.332 | 1.535 |
| **Peak year** | 1 | 2 | **5** | 5 | 5 |
| **Break-even year** (when it declines) | 2 | 2 | **3** | 4 | 5 |
| **Final employment (year 5)** | 0.761 | 0.928 | **1.131** | 1.331 | 1.535 |

- **Employment never declines in 52.4% of runs** — over a 5-year window, employment
  grows the whole way through in a slight majority of scenarios.

### What this says
- The **typical (median) path** sees employment climb to **~1.14× today's level**, with
  the peak most often landing at **year 5** (the end of the window) — i.e. still rising
  when the simulation stops.
- The **range is much narrower than over 10 years**: by year 5 the middle-80% band runs
  from **0.76× (a 24% contraction)** to **1.54× (a 54% expansion)**. The deep contraction
  scenarios that appear later in a 10-year run haven't had time to materialize.

---

## 1a. Year-3 snapshot — demand vs. productivity

The break-even race plays out over time, so the early years look different from the end.
Looking specifically at **year 3** (extracted with `year3_analysis.py`, which replays the
identical MC draw — seed 42, same parameter order). *Year-3 dynamics are independent of
the simulation horizon, so these figures match the earlier 10-year report.*

| | Productivity grows **≥** demand | Demand wins (Jevons holds) |
|---|---|---|
| **Year 3** | **30.1%** of runs | 69.9% |
| **Year 5 (final)** | ~45.9% of runs | 54.1% |

**At year 3, productivity grows as fast or faster than demand in only 30.1% of runs**
(301 of 1,000 — all strictly faster; exact ties have effectively zero probability with
continuous draws). In the other **69.9%**, demand is still outrunning productivity.

Year-3 growth-rate distribution:

| Quantity | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Demand growth (%/yr) | — | — | **9.7** | — | — |
| Productivity growth (%/yr) | — | — | **7.5** | — | — |
| Margin (Demand − Productivity, %/yr) | −3.4 | −0.6 | **+2.8** | +6.5 | +11.1 |

### What this says
The median year-3 margin is **+2.8%/yr** (demand winning). By year 5 the median margin is
roughly flat (**+0.6%/yr**, see §2), as productivity gains begin to catch up. Within a
5-year window, **demand is still winning at year 3 for ~70% of scenarios**, and the field
is much more even by the final year — but the full productivity-dominance regime seen in
the 10-year run does not arrive inside 5 years.

---

## 2. The break-even margin (year 5, final year)

Employment direction is governed by a race between two forces:
**demand growth** (more software wanted) vs. **productivity growth** (each engineer
does more). The difference between them is the **margin**.

| Quantity | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Demand growth (%/yr) | 7.2 | 10.0 | **13.8** | 17.2 | 20.0 |
| Productivity growth (%/yr) | 5.9 | 9.2 | **13.0** | 17.1 | 21.6 |
| **Margin (Demand − Productivity, %/yr)** | −7.8 | −4.1 | **+0.6** | +5.0 | +9.0 |

- **Jevons paradox holds (demand outruns productivity) in 54.1% of runs** at year 5.

### What this says
- In the **median** run at year 5, demand growth (13.8%/yr) **just edges out** productivity
  growth (13.0%/yr), giving a slightly positive margin of **+0.6%/yr**. Employment is still
  marginally rising at the end of the window.
- This is a very different picture from the 10-year horizon, where productivity had pulled
  decisively ahead (median margin −5.0%/yr). **Within 5 years, the demand-driven "Jevons"
  effect is still winning slightly more often than not** — productivity hasn't yet matured
  enough to dominate.

---

## 3. Verdicts — how often does each outcome occur?

Share of the 1,000 runs ending in each state at year 5:

| Outcome at year 5 | Share of runs |
|---|---|
| Final employment **> baseline (1.0×)** — net job growth | **66.4%** |
| Final employment **> 1.1×** — clear expansion | 53.2% |
| Final employment **< 0.9×** — clear contraction | 20.9% |
| Final employment **< 0.7×** — severe contraction | 7.4% |

### What this says
Over a 5-year window the balance **tilts clearly toward growth**: about **two-thirds of
scenarios (66.4%) end with more engineers than today**, and a clear expansion (53.2%) is
far more common than a clear contraction (20.9%). Severe contraction below 0.7× is rare
(7.4%). This is the key effect of the shorter horizon — the destructive tail that the
10-year run produced (where ~38% fell below 0.7×) largely hasn't had time to develop. The
near-term story is mostly expansionary; the divergent, more extreme outcomes are a
longer-run phenomenon.

---

## 4. What drives the outcome — parameter influence

Pearson correlation between each drawn parameter and final (year-5) employment.
Sign shows direction; magnitude shows strength.

| Parameter | Correlation | Effect on employment |
|---|---|---|
| `labor.g_tools` (tool capability growth rate) | **−0.564** | ↑ tool power → **fewer** engineers (strongest driver) |
| `context.annual_cost_reduction_rate` | +0.480 | ↑ cheaper compute/context → more engineers |
| `demand.underserved_threshold` | −0.342 | ↑ → fewer engineers |
| `demand.agentic_expansion_rate` | +0.207 | ↑ → more engineers |
| `demand.backlog_initial_months` | +0.178 | ↑ starting backlog → more engineers |
| `adoption.initial_adoption` | −0.170 | ↑ faster initial uptake → fewer engineers |
| `labor.alpha_experienced` | −0.162 | ↑ → fewer engineers |
| `labor.alpha_routine` | −0.153 | ↑ routine automation → fewer engineers |

### What this says
- **The single most important lever is still `g_tools`** — how fast agentic coding tools
  grow in capability (r = −0.56). Faster tools → fewer engineers.
- At the 5-year horizon, **`annual_cost_reduction_rate` rises to near-equal importance**
  (r = +0.48, up from +0.29 over 10 years): in the near term, how cheap compute/context
  gets is a powerful expansionary force, because it drives demand before productivity has
  matured enough to shed headcount.
- Crucially, **the strongest driver (`g_tools`) has no empirical basis** in the model —
  it's an assumption. So the spread above is honest: the outcome hinges most on the
  parameter we know the least about.

---

## 5. Bottom line

1. **Over 5 years the model leans expansionary.** Median employment rises to ~1.14×, two
   thirds of runs end above today's baseline, and employment never declines in 52% of runs.
2. **The race is close but demand is slightly ahead** at year 5 (median margin +0.6%/yr;
   Jevons holds in 54% of runs). Productivity has not yet matured enough to dominate.
3. **The severe-contraction tail is a longer-run phenomenon.** Within 5 years only 7% of
   runs fall below 0.7×, versus ~38% over 10 years — the divergent, extreme outcomes need
   more time to develop.
4. **The deciding factors are how fast tools get more capable (`g_tools`) and how fast
   compute/context costs fall (`annual_cost_reduction_rate`)** — the latter is especially
   influential in the near term.
5. **Treat the spread as a map of our ignorance**, not a probability of the future — the
   biggest driver is also the least empirically grounded parameter.

---

*Generated from `market_model/core/monte_carlo.py` at a 5-year horizon
(`context.simulation_years: 5`). Reproduce with:*
`python run.py --monte-carlo --iterations 1000`
