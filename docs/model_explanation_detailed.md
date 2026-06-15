# Agentic Coding Labor Model v5: Detailed Technical Explanation

## 1. Purpose and Scope

This model estimates the effect of agentic coding tools on software engineer
employment over a ten-year simulation horizon. It operates at two levels:

  MARKET LEVEL: What happens to aggregate software engineer employment as
  agentic coding reduces the unit cost of producing software?

  FIRM LEVEL: Given a specific firm's characteristics, what happens to its
  engineering headcount? How does the management decision about whether to
  harvest efficiency gains or reinvest them determine the outcome?

This is a reasoning tool, not a forecasting tool. Its primary value is
forcing assumptions to be made explicit, identifying which parameters drive
the outcome, and showing the range of plausible trajectories under different
assumptions. It should not be used to produce precise headcount forecasts.

---

## 2. Model Architecture

Three structural layers:

  LAYER 1: MARKET MODEL (production function equilibrium)
    Dynamic demand stocks with inflows/outflows (backlog, technical debt)
    Saturating demand components (underserved markets deplete, induced demand
    has finite size, aggregate ceiling via tanh saturation)
    Bass diffusion for tool adoption dynamics
    Break-even analysis as primary output (not employment index)

  LAYER 2: COGNITIVE EXTENSION (V5)
    Three-component alpha (task-substitution drag, routine gains, cognitive gains)
    Cognitive scope expansion separate from f_auto (slower, lower ceiling)
    Cognitive leverage tier multipliers (senior benefits more, junior less)

  LAYER 3: FIRM MODEL
    Four-way management fork (Harvest, Reinvest, Expand, Improve)
    Dynamic firm backlog stock (V5 fix: replaces permanent static boost)
    Revenue saturation by market penetration
    Organizational absorption cap (35%/yr maximum headcount growth)

---

## 3. Primary Output: Three Numbers

The model leads with a trajectory shape, not a point estimate:

  PEAK EMPLOYMENT: max employment index above baseline during simulation
  BREAK-EVEN YEAR: first year employment starts declining from peak
  FINAL EMPLOYMENT: employment level at year 10

Base scenario results:
  Peak: 1.112× baseline  (year 4)
  Break-even: year 5
  Final: 1.023× baseline  (year 10)

Read as: engineers peak at 11% above baseline by year 4, start declining
in year 5 as productivity growth overtakes demand growth, end at 2.3%
above baseline in year 10.

The break-even year is the most decision-relevant single number. It answers:
how long does the window of rising engineer employment last?

---

## 4. Productivity Model (V5: Three-Component Alpha)

### 4.1 Components

  g_productivity(t) = tool_gain(t) + routine_gain(t) + cognitive_gain(t)
                    - verification_drag(t) - debt_drag(t)

#### Tool improvement gain
  = [(1 + g_tools)^t / (1 + g_tools)^(t-1) - 1] x adoption_fraction
  ≈ g_tools × adoption_fraction

  g_tools = 0.20 (20%/yr capability improvement). NO EMPIRICAL BASIS.
  This is the single most impactful uncalibrated parameter.

#### Routine task gain (V4 component)
  maturity = min(1.0, t / alpha_maturation_years)
  alpha(t) = (1 - maturity) × alpha_experienced + maturity × alpha_routine
  f_auto(t) = min(0.70, f_auto × (1 + 0.04 × t))
  routine_gain = (f_auto(t) × alpha(t) - verification_drag) × adoption

  alpha_experienced = -0.19  MEDIUM confidence: METR RCT (Becker et al. 2025,
    arXiv 2507.09089). 16 developers, 246 tasks. Tools SLOWED experienced devs.
  alpha_routine = +0.20  LOW-MEDIUM: BIS field experiment, Copilot studies.
  alpha_maturation_years = 5.0  LOW confidence: structural assumption.
  f_auto = 0.35  MEDIUM: McKinsey 2023, Stack Overflow 2024 (N=65,437).

  The blend shifts from the METR drag regime to routine gains over 5 years.
  This produces low productivity growth early (1-3%/yr in years 1-3)
  rising steeply as tools mature and adoption compounds (18-20%/yr by year 10).

#### Cognitive task gain (V5 addition)
  cognitive_scope(t) = cognitive_scope_max × (1 - exp(-cognitive_growth_rate × t))
  cognitive_alpha(t) = alpha_cognitive × min(1.0, t / cognitive_maturation_years)
  cognitive_gain = f_cognitive × cognitive_scope(t) × cognitive_alpha(t) × adoption

  alpha_cognitive = 0.15   NO EMPIRICAL BASIS
  cognitive_scope_max = 0.30   NO EMPIRICAL BASIS (conservative ceiling)
  cognitive_growth_rate = 0.15   NO EMPIRICAL BASIS
  cognitive_maturation_years = 8.0   NO EMPIRICAL BASIS
  f_cognitive = 0.35   NO EMPIRICAL BASIS (estimated from task time studies)

  Four cognitive capabilities being modeled:
    Specification and decomposition (breaking problems into pieces)
    Context synthesis across large codebases
    Debugging hypothesis generation
    Requirements formalization

  Setting cognitive_scope_max = 0.0 reproduces V4 exactly (scenario: cognitive_off).

### 4.2 Why Productivity Is Low Early

In year 1: adoption = 17.5%, maturity = 0.20, alpha ≈ -0.11 (mostly METR drag)
  tool_gain = 0.20 × 0.175 = 3.5%
  routine_gain ≈ -1.0% (negative because METR drag dominates)
  cognitive_gain ≈ 0% (tools not yet assisting cognitive work)
  net g_productivity ≈ 1.3%/yr

In year 10: adoption = 72%, maturity = 1.0, alpha = +0.20 (fully routine)
  tool_gain = 0.20 × 0.719 = 14.4%
  routine_gain ≈ 5.4%
  cognitive_gain ≈ 0.9%
  net g_productivity ≈ 20%/yr

The jump from 1.3% to 20% over 10 years is driven equally by:
  (a) adoption growing from 17% to 72%
  (b) alpha shifting from negative to positive as tools mature

---

## 5. Demand Model (V5 Dynamic Stocks)

All demand components return values in "annual fraction of baseline engineering
output" — the same unit as g_productivity, making them directly comparable.

### 5.1 Backlog (dynamic stock with Parkinson refill)

  B(t+1) = B(t) + inflow(t) - outflow(t)
  inflow = baseline_inflow + parkinson × productivity_gain × B
         + agentic_expansion × adoption × B_initial
  outflow = min(B × completion_rate × (1 + productivity_gain), B - floor)

  demand_signal = (outflow - baseline_eq_outflow) / 12
               = extra work done this year vs no-agentic baseline

  parkinson_coefficient = 0.25  (was 0.40 in V4; lowered as more defensible)
  Parkinson: 25% of freed capacity immediately fills with new scope demands.
  NO EMPIRICAL BASIS.

  Note: demand and productivity both scale with adoption, which is why they
  track each other closely and the margin stays near zero for many years.

### 5.2 Technical Debt (dynamic stock with AI premium)

  TD(t+1) = TD(t) + inflow(t) - repayment(t)
  inflow = debt_per_unit_output × output × (1 + ai_debt_premium × adoption)
  demand_signal = refactoring work from repayment (POSITIVE only)

  ai_debt_premium = 0.35  MEDIUM confidence: CMU SEI 2024.
  AI-generated code creates ~35% more technical debt per line than human code.

  initial_pct = 40%  HIGH confidence: McKinsey 2023, SO Survey 2024.
  Debt affects productivity via debt_drag = TD × 0.0003 per pct-point.
  At 40% initial debt: 1.2%/yr drag (falls as debt repays).

### 5.3 Underserved Markets (depleting stock)

  U(t+1) = U(t) - penetration(t)
  penetration = U(t) × 0.12 × activation(t)
  activation = min(1, (cum_cost_reduction - 0.40) / 0.40)

  Only activates after 40% cumulative cost reduction (≈ year 5 at base rate).
  Then depletes at 12%/yr of remaining stock.

  underserved_fraction = 0.25  NO EMPIRICAL BASIS.
  threshold = 0.40  NO EMPIRICAL BASIS.

### 5.4 Induced Demand (finite Bass diffusion)

  New software categories that don't currently exist. Finite total size.
  Follows Bass diffusion (p=0.02, q=0.30, start_year=3).
  Total size = induced_market_size = 0.20  NO EMPIRICAL BASIS.

### 5.5 Price Elasticity (cumulative cap)

  expansion = weighted_elasticity × annual_price_reduction
  Weighted: consumer=1.80, SMB=1.40, enterprise=0.45, regulated=0.20.
  Cumulative cap: max_cumulative_expansion = 0.60 (Baumol constraint).

  MEDIUM confidence on elasticity values: industry pricing research.

### 5.6 Aggregate Ceiling

  D_saturated = D_max × tanh(D_raw / D_max), D_max = 3.0
  Annual demand capped at D_max × 0.20 per year.

---

## 6. Technology Adoption: Bass Diffusion

  F(t) = (1 - e^(-(p+q)t)) / (1 + (q/p) × e^(-(p+q)t))

  p = 0.03, q = 0.38, initial_adoption = 0.15, max_adoption = 0.85

  LOW confidence: fitted approximately to GitHub Copilot adoption 2021-2024.

  Adoption is the common multiplier on both demand and productivity.
  When adoption doubles (17%→72% over 10 years), both sides roughly double.
  This co-movement keeps the margin small and the race close.

---

## 7. Break-Even Sensitivity Analysis

Run with:
  python run.py --breakeven-sensitivity
  python run.py --crossplot

Cross-plot: break-even year as f(g_tools, parkinson_coefficient)

  g_tools \ parkinson   0.15   0.25*  0.35   0.45
  g_tools=0.10         never  never  never  never
  g_tools=0.15          yr9   never  never  never
  g_tools=0.20*         yr4    yr5    yr8   never
  g_tools=0.25          yr4    yr4    yr4    yr4
  g_tools=0.30          yr3    yr4    yr4    yr4
  g_tools=0.35          yr3    yr3    yr3    yr3

  * = base parameters

Full uncertainty range: break-even year spans 3 to "never within 10 years."
The model is appropriately agnostic. It identifies what to watch, not what
will happen. Neither g_tools nor parkinson_coefficient has empirical basis.

---

## 8. Exogenous Multiplier

  E = geometric_mean(gdp^0.35, immigration^0.25, education^0.20, regulation^0.20)
  Scale: [0.5, 2.0], centered on 1.0
  Applied to net employment delta: I_final = 1 + (I_structural - 1) × E

  Geometric mean: a 50% immigration boost and 50% regulatory drag cancel.
  HIGH confidence for GDP sub-component (IMF data). LOW for all others.

---

## 9. Firm Model

### 9.1 Four-Way Management Fork

  HARVEST:  Reduce headcount. Same output, better margin.
  REINVEST: Flat headcount. More output, grow revenue.
  EXPAND:   Grow headcount. New projects newly viable at lower cost.
  IMPROVE:  Flat headcount. Use gains for quality/debt (V4 addition).

Fork is classified from observable firm characteristics. Most firms blend.
IMPROVE is driven by: high technical debt (>45%), regulated industry, active
legacy modernization, high current market penetration.

### 9.2 Dynamic Firm Backlog (V5 fix — most important firm model change)

PREVIOUS (V4): static permanent boost
  backlog_boost = min(0.40, backlog_months/30)  [never changed]

V5 FIX: FirmBacklogStock with depletion and Parkinson refill
  B(t+1) = B(t) - net_clearance(t)
  net_clearance = completion × (1 - firm_parkinson)
  completion = B × 1.5 × (1 + productivity_gain)
  demand_factor = max(0, B/B_initial - floor/B_initial)  [fades to 0]
  backlog_boost = min(0.40, demand_factor × 0.40)

Firm-specific Parkinson coefficients (industry defaults, NO EMPIRICAL BASIS):
  consumer_tech: 0.45  enterprise_saas: 0.30  fintech: 0.20
  healthcare: 0.15  manufacturing: 0.15  government: 0.10

Impact: a consumer startup with 18 months of backlog now grows from 50 to
62 engineers (not 142 as in V4). The backlog demand fades by year 5 as
it is worked through, and only the Parkinson refill rate sustains ongoing demand.

Optional profile field: firm_parkinson_override to set a specific value.

### 9.3 Revenue Saturation (V4, maintained in V5)

  g(t) = long_run_rate + (initial_rate - long_run_rate) × exp(-λ × t × penetration)

High current_market_penetration → fast decay toward long-run growth rate.
Low penetration → slow decay; high growth persists longer.

Required new profile fields: long_run_growth_rate, current_market_penetration.

### 9.4 Organizational Absorption Cap

  headcount_growth(t) = min(uncapped_growth(t), prev_index × 1.35)

Maximum 35%/yr headcount growth from EXPAND strategy. Engineering orgs cannot
hire and productively onboard faster (onboarding time, code review bandwidth,
coordination overhead).

### 9.5 Cognitive Leverage in Tier Adjustments (V5)

  tier_index = base_index × (1 + (leverage - 1) × cognitive_scope)

  leverage factors (NO EMPIRICAL BASIS):
    architect: 1.60  senior: 1.40  mid: 1.10  junior: 0.70

Junior leverage < 1.0 is the key V5 insight: cognitive tools require domain
expertise to direct. A junior engineer doesn't yet know what architectural
question to ask. Cognitive tools widen the gap between senior and junior
employment, not narrow it.

At cognitive_scope = 0: reverts exactly to V4 tier adjustments.

---

## 10. Empirical Confidence Summary

HIGH confidence:
  tech_debt_initial_pct = 0.40  (McKinsey 2023; SO Survey 2024 N=65,437)
  market growth baseline = 8%/yr  (BLS Nov 2025)

MEDIUM confidence:
  alpha_experienced = -0.19  (METR RCT 2025; N=16, specific context)
  f_auto = 0.35  (McKinsey 2023; SO Survey 2024)
  price_elasticity by segment  (industry pricing research)
  ai_debt_premium = 0.35  (CMU SEI 2024)
  Bass q = 0.38  (fitted to Copilot 2021-2024)

LOW confidence:
  alpha_routine = 0.20  (non-RCT studies)
  alpha_maturation_years = 5.0  (structural assumption)
  backlog_initial_months = 6.0  (proxy from sprint data)
  consumer_capture_rate  (IO theory applied to software)

NO EMPIRICAL BASIS (must be varied in sensitivity analysis):
  g_tools = 0.20                    Most impactful uncalibrated parameter
  parkinson_coefficient = 0.25      Second most impactful
  f_verify = 0.25
  annual_cost_reduction_rate = 0.12
  phi = 0.85
  underserved_fraction = 0.25
  induced_market_size = 0.20
  alpha_cognitive = 0.15            V5 cognitive
  cognitive_scope_max = 0.30        V5 cognitive
  cognitive_growth_rate = 0.15      V5 cognitive
  cognitive_maturation_years = 8.0  V5 cognitive
  firm Parkinson coefficients       Judgment-based industry defaults

---

## 11. What the Model Cannot Do

1. Predict aggregate employment precisely — too many uncalibrated parameters.
2. Model transition frictions — hiring lags, reskilling time, supply response.
3. Separate AI effects from macroeconomic cycle effects in near-term data.
4. Account for structural breaks — capability discontinuities, regulatory shocks.
5. Determine which fork a specific firm will take — fork is a hypothesis,
   not a measurement of management intent.
6. Validate the cognitive component — no empirical basis exists for V5's
   alpha_cognitive, scope_max, growth_rate. Run cognitive_off to test sensitivity.

---

## 12. Version History

V1: System dynamics — compounding effects producing nonsensical results (55× index).
V2: Structural decomposition + Jevons condition. Empirical calibration doc.
    Exogenous multiplier. Firm model with heuristic multipliers.
V3: Break-even analysis as primary output. Bass diffusion. Three-way fork.
V4: Dynamic demand stocks. Underserved markets deplete. Induced demand bounded.
    Aggregate ceiling. Revenue saturation. IMPROVE fork. Absorption cap (35%/yr).
V5: Three-component alpha (cognitive). Cognitive scope expansion. Cognitive
    leverage by tier. Parkinson 0.40→0.25. alpha_maturation_years parameterized.
    Break-even sensitivity analysis + cross-plot. FirmBacklogStock (depletion +
    Parkinson refill). Firm-specific Parkinson by industry.
