# Agentic Coding Labor Model v4: Detailed Technical Explanation

## 1. What the Model Is For

This model estimates the effect of agentic coding tools on software engineer employment,
at both a market (aggregate) level and a firm level. It is a reasoning tool, not a
forecasting tool. Its primary output is a break-even analysis: given what we know about
demand, how fast would productivity need to grow before engineer employment starts falling?
Its secondary output is a directional employment index.

The model was built iteratively, with each version correcting structural errors in
the previous one. Version 4 makes the following fundamental corrections over v3:

  - Backlog and technical debt are modeled as dynamic stocks with inflows and outflows,
    not one-time stocks that exhaust to zero
  - All demand components have saturation mechanisms preventing indefinite growth
  - Underserved markets deplete as they are penetrated
  - Induced demand has a finite total size governed by a Bass diffusion curve
  - The firm model adds revenue saturation, an organizational absorption cap, and an
    explicit IMPROVE branch to the management decision fork

---

## 2. Core Architecture

### 2.1 The Production Function

The model is grounded in a software production function:

  S(t) = A(t) × E(t)^phi

where:
  S(t)   = software output at time t (index, baseline = 1.0)
  A(t)   = total factor productivity (captures agentic tool effectiveness)
  E(t)   = engineer headcount (index, baseline = 1.0)
  phi    = output elasticity of engineers (0 < phi <= 1; default 0.85)

phi < 1 reflects diminishing returns: doubling engineers does not double output,
because coordination costs, communication overhead, and sequential dependencies
(Brooks' Law) mean the relationship is sublinear.

Setting supply equal to demand and solving for equilibrium headcount:

  E*(t) = (D(t) / A(t))^(1/phi)

where D(t) is the demand ratio: how much software the market wants, relative to
the no-agentic-coding baseline.

### 2.2 The Break-Even Condition

Employment is flat when dE*/dt = 0, which requires:

  d(ln D)/dt = d(ln A)/dt

In words: demand must grow at the same rate as productivity for employment to be flat.
If demand grows faster than productivity, employment rises (Jevons holds).
If productivity grows faster than demand, employment falls (Jevons fails).

The break-even productivity growth rate is therefore:

  g*_productivity = g_demand

This is the primary output: given our best estimate of demand growth (which has
more empirical grounding), what productivity growth rate would make employment flat?
If actual productivity growth exceeds g*, Jevons fails.

### 2.3 Why Break-Even Analysis Is the Primary Output

The demand side has meaningful empirical grounding:
  - Technical debt fraction: HIGH confidence (McKinsey 2023, Stack Overflow 2024)
  - Price elasticity: MEDIUM confidence (industry pricing research)
  - Market baseline growth: HIGH confidence (BLS Occupational Outlook)

The productivity side has almost no empirical grounding:
  - Tool improvement rate (g_tools): NO empirical basis
  - Verification overhead: NO empirical basis
  - Future capability trajectory: NO empirical basis

Asking "what would productivity need to be?" tells practitioners what to watch,
without requiring them to trust uncalibrated parameters.

---

## 3. Demand Model (v4 Corrections)

### 3.1 Overview

The demand model computes D(t): the ratio of software demand under agentic coding
to what it would have been without. D(t) = 1.0 means no change; D(t) = 1.5 means
50% more software demanded.

D(t) has five components. Each is modeled correctly as either a stock (finite, depletes
and accumulates) or a flow (ongoing, but with a saturation ceiling):

  D(t) = 1 + elasticity_demand(t) + backlog_demand(t)
           + debt_demand(t) + underserved_demand(t) + induced_demand(t)

All five components are subject to an aggregate ceiling so D(t) cannot grow without bound.

### 3.2 Backlog: Dynamic Stock with Equilibrium (KEY CORRECTION FROM v3)

**What was wrong in v3:** Backlog was treated as a one-time stock that depleted
to zero by year 5. This was wrong in two ways:
  1. Backlog never goes to zero — organizations always generate new work faster
     than they can complete it; some backlog is structurally permanent
  2. Backlog accumulates continuously — as the business grows and as agentic tools
     open new possibilities, new work enters the backlog faster

**How v4 models it:**

The backlog is a stock B(t) with explicit inflows and outflows:

  B(t+1) = B(t) + inflow(t) - outflow(t)

  inflow(t) = B_baseline_inflow                    # normal business demand
            + B_parkinson × productivity(t)         # Parkinson's Law: capacity fills
            + B_agentic_expansion × adoption(t)     # new projects now feasible

  outflow(t) = completion_rate(t)                  # function of engineer productivity

  completion_rate(t) = B(t) × (1 + productivity_gain(t)) / B_clearance_halflife

The equilibrium backlog is where inflow = outflow. When productivity rises:
  - outflow rises (backlog clears faster)
  - BUT inflow also rises (Parkinson's Law: more capacity → more scope demanded)
  - The net change in equilibrium backlog is smaller than a naive model suggests

The demand signal from backlog is the excess above equilibrium:
  backlog_demand(t) = max(0, B(t) - B_equilibrium(t)) / B_baseline

**Floor:** B(t) never falls below `backlog_floor_months` (default 2 months),
reflecting the structural minimum — organizations always have more ideas than capacity.

**Empirical note:** No direct measurement of backlog equilibrium dynamics exists.
The Parkinson coefficient is a model assumption. The equilibrium concept is grounded
in organizational theory but not calibrated to data.

### 3.3 Technical Debt: Dynamic Stock with AI Premium (KEY CORRECTION FROM v3)

**What was wrong in v3:** Technical debt was treated as a one-time stock that
depleted and then became a slight negative by year 5. This ignored:
  1. New debt accumulates continuously with every feature shipped
  2. AI-generated code creates more debt per line than human-written code
     (CMU SEI 2024: ~35% more technical debt from AI-assisted code)
  3. Some debt is structural and never gets addressed

**How v4 models it:**

The debt stock TD(t) evolves as:

  TD(t+1) = TD(t) + debt_inflow(t) - debt_repayment(t)

  debt_inflow(t) = base_inflow_rate × output(t)       # proportional to what's shipped
                 × (1 + ai_debt_premium × adoption(t)) # AI code is higher debt/line
                 × (1 - quality_investment_rate)        # some orgs invest in quality

  debt_repayment(t) = TD(t) × repayment_rate(t)
    where repayment_rate(t) = base_repayment_rate
                            × (1 + productivity_gain(t) × debt_focus_fraction)

  structural_floor = TD_initial × debt_floor_fraction  # debt that never gets addressed

The demand signal from technical debt is the current maintainability burden:
  debt_demand(t) = -debt_maintenance_fraction × TD(t)  # negative: debt consumes capacity

**Note:** Technical debt generates NEGATIVE demand in the long run — it consumes
engineering capacity that could otherwise be used for new features. Near-term,
addressing debt generates positive demand (refactoring work). Medium-term, clean
code reduces maintenance burden. The current model correctly captures this arc.

**The AI debt premium is important:** When agentic adoption is high, output grows
but so does debt inflow. This partially offsets the productivity gain and explains
why the net employment effect of agentic coding may be smaller than naive productivity
estimates suggest.

### 3.4 Underserved Markets: Penetration-Depleting Stock (CORRECTION FROM v3)

**What was wrong in v3:** The underserved market activated past a cost threshold
and kept generating demand indefinitely. The market never depleted as it got served.

**How v4 models it:**

The underserved market is a finite stock U(t) that depletes as it gets penetrated:

  U(t+1) = U(t) - penetration(t)

  penetration(t) = U(t) × penetration_rate(t)

  penetration_rate(t) = 0                           if cost_reduction < threshold
                      = base_penetration_rate        if cost_reduction >= threshold
                        × activation(t)              # ramp in as cost falls further

  activation(t) = min(1, (cost_reduction - threshold) / threshold)

The demand signal is the flow of newly penetrated market:
  underserved_demand(t) = penetration(t) / U_initial

As U(t) → 0, this demand source exhausts. The total cumulative demand from
underserved markets is bounded by U_initial (the initial underserved fraction).

### 3.5 Induced Demand: Bass Diffusion on New Categories (CORRECTION FROM v3)

**What was wrong in v3:** Induced demand (new software categories that don't yet
exist) grew via an S-curve on the annual rate, but the cumulative stock kept
growing without a ceiling. There was no total size on the new market created.

**How v4 models it:**

Induced demand is modeled as a new market that itself follows Bass diffusion:

  The total size of new categories created = induced_market_size (parameter)
  The penetration of those new categories follows: F(t) = Bass(p_induced, q_induced, t)

  induced_demand(t) = induced_market_size × F(t)    # level of new market demand

The annual demand signal is the first difference:
  induced_flow(t) = induced_demand(t) - induced_demand(t-1)   # growth rate

This correctly models induced demand as: new categories appear (slowly at first,
then rapidly, then tapering) and eventually reach their own market saturation.
The total lifetime demand from induced effects is bounded.

### 3.6 Price Elasticity: Cumulative Cap (CORRECTION FROM v3)

The elasticity-driven demand expansion has a cumulative ceiling:

  elasticity_demand_cumulative(t) = min(
      cumulative_elasticity_demand(t),
      max_market_expansion × baseline_D   # hard ceiling: market can at most N× baseline
  )

  max_market_expansion = 2.0 (default): software market can at most double from agentic
  effects above baseline growth. This reflects the Baumol constraint: as software gets
  cheaper, other inputs (PM, design, sales, CS) become the binding constraint.

### 3.7 Aggregate Demand Ceiling

After summing all components, a logistic saturation is applied:

  D_saturated(t) = D_max / (1 + exp(-k × (D_raw(t) - D_inflection)))

where D_max is the maximum plausible demand ratio (default 3.0: demand triples at most),
and k controls the steepness of saturation.

This prevents the physically impossible case of demand growing without bound as
costs approach zero.

---

## 4. Productivity Model

### 4.1 Total Factor Productivity

A(t) captures how much software one engineer can produce, modulated by:
  - Tool capability at time t (grows at g_tools per year)
  - Adoption fraction F_adoption(t) from Bass diffusion
  - Task composition: what fraction of tasks are automatable
  - Verification overhead: the cost of reviewing AI-generated output
  - Debt drag: accumulated technical debt slows productivity regardless of tools

  A(t) = A_baseline × (1 + net_gain(t) × F_adoption(t))

  net_gain(t) = f_auto(t) × alpha(t)                    # automation gain
              - f_verify × f_auto(t) × verification_drag # verification drag
              - debt_drag(t)                             # debt maintenance burden

  alpha(t) = blend of alpha_experienced (METR: -0.19) and alpha_routine (+0.20)
             weighted by tool maturity: matures from experienced-dev context
             toward routine-task gains over 5 years

  debt_drag(t) = TD(t) × debt_productivity_drag_rate     # debt slows everyone

### 4.2 Technology Adoption: Bass Diffusion

The fraction of engineers using mature agentic tools follows:

  F_adoption(t) = Bass(p=0.03, q=0.38, initial=0.15, max=0.85)

Key insight: productivity effects are muted in early years because most engineers
haven't adopted tools yet, even if the tools are capable. The adoption curve drives
the timing of productivity effects more than the raw capability does.

---

## 5. Exogenous Multiplier

Four factors outside the structural model are bundled into a single composite:

  E = geometric_mean(gdp^w1, immigration^w2, education^w3, regulation^w4)

  Weights: gdp=0.35, immigration=0.25, education=0.20, regulation=0.20
  Scale: [0.5, 2.0], centered on 1.0

  Applied to net employment delta: I_final(t) = 1 + (I_structural(t) - 1) × E

Geometric mean is used because these are multiplicative effects. A 50% boost from
favorable immigration and a 50% drag from restrictive regulation should roughly cancel —
geometric mean captures this (1.5 × 0.67 ≈ 1.0); arithmetic mean would not.

---

## 6. Firm Model: Three-Way Management Fork + IMPROVE Branch

### 6.1 The Four Strategies

When agentic coding raises engineer productivity, management chooses among:

  HARVEST:  Reduce headcount, maintain output, capture efficiency as margin
  REINVEST: Maintain headcount, produce more/better software, grow revenue
  EXPAND:   Increase headcount, pursue projects previously not viable at old cost
  IMPROVE:  Maintain headcount, raise quality rather than quantity (NEW IN V4)

Most firms blend these strategies. The model classifies the primary strategy
from observable firm characteristics and allows weighted blends.

### 6.2 Fork Classification Logic

Observable inputs from firm profile drive fork classification:

  HARVEST score ↑ when:
    software_is_core_product = False (cost center)
    competitive_intensity = low
    capital_efficiency_pressure = high
    backlog_months < 3 (no pent-up demand)
    will_pass_savings_to_customers = False + low competition

  REINVEST score ↑ when:
    software_is_core_product = True
    competitive_intensity = medium
    backlog_months 3-9

  EXPAND score ↑ when:
    will_pass_savings_to_customers = True
    competitive_intensity = high
    backlog_months > 9
    revenue_growth_rate > 0.20

  IMPROVE score ↑ when (NEW IN V4):
    technical_debt_pct > 45 (high debt: quality investment has high ROI)
    industry in [healthcare, fintech, regulated] (quality constraints dominate)
    has_legacy_modernization = True (already in quality-improvement mode)
    current_market_penetration > 0.30 (mature product: users want quality, not features)

### 6.3 Revenue Saturation (CORRECTION FROM v3)

v3's EXPAND branch let revenue growth compound indefinitely. v4 replaces this with
a logistic saturation tied to market penetration:

  growth_rate(t) = long_run_growth_rate
                 + (initial_growth_rate - long_run_growth_rate)
                   × exp(-saturation_rate × t × current_market_penetration)

where:
  long_run_growth_rate = max(gdp_growth, industry_baseline)  # e.g., 0.06
  saturation_rate      = function of market_penetration_rate
  current_market_penetration = fraction of TAM already captured (firm profile input)

High penetration → fast decay toward long-run rate.
Low penetration → slow decay; high growth persists longer.

### 6.4 Organizational Absorption Cap (NEW IN V4)

Engineering organizations cannot hire and productively onboard arbitrarily fast:
  - New engineers take 3-6 months to become productive
  - Code review bandwidth limits how fast new contributors can ship
  - Coordination overhead (Brooks' Law) grows superlinearly

v4 caps the year-on-year headcount growth from EXPAND at 35%:
  headcount_growth(t) = min(uncapped_growth(t), 0.35)

This is the most conservative parameter in the firm model. It reflects the
observed fact that even well-funded, fast-growing engineering organizations
rarely sustain >30-35% headcount growth for multiple consecutive years.

### 6.5 IMPROVE Branch Headcount Implications (NEW IN V4)

IMPROVE means productivity gains are absorbed into quality, not quantity:
  - No headcount reduction (unlike HARVEST)
  - No output quantity increase (unlike REINVEST)
  - Headcount stays approximately flat, with slight growth for senior engineers
    needed to architect quality improvements

  h_improve(t) = 1.0 + 0.05 × min(1.0, t/5.0)   # slight senior growth

IMPROVE is important because it explains a real-world phenomenon the other branches
miss: many firms will neither cut engineers nor grow them — they'll use the productivity
gain to finally fix things they've deferred. The model should be able to represent this.

### 6.6 Technical Debt Feedback in Firm Model

The firm's technical_debt_pct evolves using the same stock-and-flow logic as the
market model. This means:
  - HARVEST firms accumulate debt faster (output maintained with fewer, more-rushed engineers)
  - EXPAND firms accumulate debt faster (shipping speed increases)
  - IMPROVE firms reduce debt (deliberate quality investment)
  - REINVEST firms are neutral on debt

The debt level feeds back into productivity: high-debt firms see lower effective
productivity gains because engineers spend more time on maintenance.

---

## 7. Parameters, Confidence, and What Cannot Be Known

### 7.1 Well-Calibrated Parameters (use with confidence)

| Parameter | Value | Source | Confidence |
|---|---|---|---|
| tech_debt_fraction | 0.40 | McKinsey 2023; SO 2024 N=65,437 | HIGH |
| alpha_experienced | -0.19 | METR RCT, Becker et al. 2025 | MEDIUM |
| market_growth_baseline | 0.08 | BLS Nov 2025 | HIGH |
| price_elasticity (enterprise) | 0.45 | Industry pricing research | MEDIUM |
| price_elasticity (consumer) | 1.80 | Industry pricing research | MEDIUM |
| Bass q (imitation) | 0.38 | Fitted to Copilot 2021-2024 | LOW |

### 7.2 Parameters With No Empirical Basis

These must be varied in sensitivity analysis. Results that depend heavily on these
should not be treated as reliable:

  g_tools (tool improvement rate), f_verify (verification overhead),
  underserved_fraction, induced_market_size, annual_cost_reduction_rate,
  phi (production function elasticity), B_parkinson (Parkinson coefficient),
  debt_ai_premium, max_market_expansion

### 7.3 The Fundamental Limit of This Model

The pivotal variable that determines whether Jevons holds or fails is:

  What fraction of productivity gains do firms reinvest in more software
  vs. harvest as cost reduction?

This is a management behavior question. It varies by firm, competitive environment,
capital markets pressure, and strategic posture. No dataset captures it. The model
represents it through the fork classification, but the fork itself is a hypothesis
about management intent derived from observable characteristics — not a measurement.

---

## 8. What the Model Cannot Do

1. Predict aggregate employment precisely — too many uncalibrated parameters
2. Model transition frictions — hiring/firing lags, skill development time
3. Account for structural breaks — sudden AI capability discontinuities
4. Separate AI effects from macroeconomic cycle in near-term data
5. Determine which fork a specific firm will choose — this requires knowing
   management intent, which is not derivable from observable characteristics alone
6. Model international trade in software or cross-border labor flows in detail

---

## 9. Historical Analogies and What They Suggest

Four historical cases where productivity-enhancing technology hit knowledge work:

CAD in mechanical engineering (1970-1990):
  Productivity gain: 3-10x on drafting. Employment: net INCREASE.
  Why: Lower iteration cost unlocked qualitatively new design possibilities.
  Lesson: When tools enable genuinely new work, Jevons holds.

Spreadsheets in accounting (1980-1990):
  Productivity gain: 5-10x on calculation. Employment: net FLAT.
  Why: More complex analysis became feasible; compliance demands grew.
  Lesson: Task expansion can absorb large productivity gains.

ATMs in banking (1970-2000):
  Productivity gain: significant per-branch cost reduction. Employment: net INCREASE in tellers.
  Why: Lower branch cost → more branches → more tellers (distribution effect).
  Lesson: Cost reduction can expand the distribution channel, growing total employment.

Word processing in secretarial work (1970-1990):
  Productivity gain: large on document production. Employment: net SHARP DECLINE.
  Why: Managers did their own typing; no demand expansion pathway.
  Lesson: When there is no demand expansion pathway and the task is routine, substitution wins.

Software engineering resembles CAD and spreadsheets more than word processing:
  - There is a large demand expansion pathway (backlog, underserved markets, new categories)
  - The work is not purely routine (architecture, requirements, judgment are hard to automate)
  - The tools open new possibilities (products that were too expensive to build before)

This suggests Jevons is more likely to hold for software engineering than fail —
but the historical analogies also show that demand expansion is not guaranteed,
and the v4 saturation mechanisms correctly prevent the model from assuming it is.
