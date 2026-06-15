# Complete Variable Documentation: Agentic Coding Labor Model v5

All variables are listed with their parameter path, description, units,
hard limits (absolute min/max), base value, and reasonable uncertainty range
for Monte Carlo simulation. Empirical confidence is documented for each.

Confidence levels:
  HIGH   — Multiple large-sample studies agree; range is tight
  MEDIUM — Some empirical data; limited sample or contested
  LOW    — Indirect proxy or structural assumption with some grounding
  NONE   — No empirical basis; pure assumption; wide range appropriate

Format per variable:
  path:        config path (dot-separated)
  base:        default value
  hard_min:    absolute lower bound (model breaks below this)
  hard_max:    absolute upper bound (model breaks above this)
  mc_low:      10th percentile for Monte Carlo draws
  mc_high:     90th percentile for Monte Carlo draws
  confidence:  HIGH / MEDIUM / LOW / NONE
  source:      empirical source or basis
  notes:       interpretation guidance

═══════════════════════════════════════════════════════════════════════
SECTION 1: CONTEXT AND PRODUCTION FUNCTION
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
1.1  context.simulation_years
─────────────────────────────────────────────────────────────────────
  path:       context.simulation_years
  base:       10
  hard_min:   1
  hard_max:   20
  mc_low:     n/a (not varied in Monte Carlo)
  mc_high:    n/a
  confidence: HIGH
  source:     Design choice; 10 years is the standard horizon for
              technology adoption and workforce planning models.
  notes:      Longer horizons amplify cumulative margin effects but
              increase parameter uncertainty. 10 years is the limit
              of meaningful scenario planning for agentic coding.

─────────────────────────────────────────────────────────────────────
1.2  context.annual_cost_reduction_rate
─────────────────────────────────────────────────────────────────────
  path:       context.annual_cost_reduction_rate
  base:       0.12  (12% per year)
  hard_min:   0.00
  hard_max:   0.50
  mc_low:     0.04
  mc_high:    0.25
  confidence: NONE
  source:     No empirical basis. Derived estimate: if agentic tools
              produce 20-55% speedup on 35% of tasks, and automatable
              fraction grows ~5%/yr, unit cost falls 7-19%/yr before
              verification overhead. Wide uncertainty.
  notes:      Drives BOTH demand (price elasticity) and productivity
              (how fast tools compound). One of the three most
              important uncertain parameters. Ranges reflect genuine
              ignorance; vary in sensitivity analysis.

─────────────────────────────────────────────────────────────────────
1.3  production.phi
─────────────────────────────────────────────────────────────────────
  path:       production.phi
  base:       0.85
  hard_min:   0.50
  hard_max:   1.00
  mc_low:     0.70
  mc_high:    0.97
  confidence: NONE
  source:     Borrowed from macroeconomic production function
              literature (Cobb-Douglas). Not validated for software.
              phi < 1 reflects diminishing returns to headcount due
              to coordination overhead (Brooks' Law).
  notes:      phi = 1.0 means each engineer contributes proportionally
              (no diminishing returns). phi = 0.7 means strong
              diminishing returns; a 10% demand increase requires
              more than 10% more engineers. The choice of phi
              significantly affects the level of the employment index
              but less so its trajectory direction.

═══════════════════════════════════════════════════════════════════════
SECTION 2: TECHNOLOGY ADOPTION (BASS DIFFUSION)
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
2.1  adoption.p  (innovation coefficient)
─────────────────────────────────────────────────────────────────────
  path:       adoption.p
  base:       0.03
  hard_min:   0.001
  hard_max:   0.15
  mc_low:     0.01
  mc_high:    0.07
  confidence: LOW
  source:     Fitted approximately to GitHub Copilot adoption
              2021-2024. Bass p for enterprise technology typically
              0.01-0.05. Developer tools may be higher due to
              individual adoption (not firm-level procurement).
  notes:      Controls how many engineers adopt without peer influence
              (early adopters). Small changes to p have modest effects
              compared to q. Primarily affects the early adoption curve.

─────────────────────────────────────────────────────────────────────
2.2  adoption.q  (imitation coefficient)
─────────────────────────────────────────────────────────────────────
  path:       adoption.q
  base:       0.38
  hard_min:   0.05
  hard_max:   0.80
  mc_low:     0.20
  mc_high:    0.55
  confidence: LOW
  source:     Fitted approximately to GitHub Copilot adoption.
              Stack Overflow 2024: 76% of developers use or plan to
              use AI tools, suggesting high imitation rate.
              Bass q for network-effect technologies typically
              0.30-0.60.
  notes:      Controls word-of-mouth adoption. Higher q → faster
              S-curve peak. This is the more impactful of the two
              Bass parameters. At q=0.55, adoption is substantially
              higher by year 5, accelerating both demand and
              productivity. Strong driver of break-even year timing.

─────────────────────────────────────────────────────────────────────
2.3  adoption.initial_adoption
─────────────────────────────────────────────────────────────────────
  path:       adoption.initial_adoption
  base:       0.15  (15%)
  hard_min:   0.00
  hard_max:   0.60
  mc_low:     0.08
  mc_high:    0.35
  confidence: LOW
  source:     Stack Overflow 2024 Developer Survey: ~30% of developers
              use AI coding tools. Discounted to 15% for "mature
              agentic" usage (beyond basic autocomplete). Uncertain
              because "mature agentic" is not precisely defined.
  notes:      Shifts the entire adoption curve. Higher initial
              adoption means earlier productivity effects and earlier
              demand response. The definition matters: daily Copilot
              users vs. occasional prompt writers.

─────────────────────────────────────────────────────────────────────
2.4  adoption.max_adoption
─────────────────────────────────────────────────────────────────────
  path:       adoption.max_adoption
  base:       0.85  (85%)
  hard_min:   0.40
  hard_max:   1.00
  mc_low:     0.70
  mc_high:    0.95
  confidence: LOW
  source:     Judgment: some safety-critical and regulated contexts
              will not adopt agentic tools at all (aerospace,
              nuclear, medical device firmware). 85% ceiling allows
              for ~15% permanent non-adoption.
  notes:      Affects the long-run plateau of productivity and demand.
              Wide uncertainty because it depends on regulatory
              evolution and risk tolerance in different industries.

═══════════════════════════════════════════════════════════════════════
SECTION 3: PRODUCTIVITY PARAMETERS
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
3.1  labor.alpha_experienced
─────────────────────────────────────────────────────────────────────
  path:       labor.alpha_experienced
  base:       -0.19  (-19% slower)
  hard_min:   -0.60
  hard_max:   +0.30
  mc_low:     -0.40
  mc_high:    +0.05
  confidence: MEDIUM
  source:     METR RCT (Becker et al., arXiv 2507.09089, July 2025).
              16 developers, 246 tasks, Claude 3.5/3.7 + Cursor Pro.
              Measured: 19% slowdown (CI: +2% to +39% slowdown) for
              experienced developers on mature, complex codebases.
              Self-reported: 20% faster (39-point gap vs. actual).
  notes:      Applies in early years when alpha_maturation_years has
              not elapsed. METR finding is specific to early-2025
              tools on complex codebases. Newer tools (Claude Opus 4,
              Claude Code) may show different results. The follow-up
              METR study using late-2025 tools is the single most
              important piece of pending empirical data for this model.
              mc_low = -0.40 (worse than METR CI) covers possibility
              that result holds or worsens with agentic workflows.
              mc_high = +0.05 covers possibility that experienced devs
              are already near neutral with 2026 tools.

─────────────────────────────────────────────────────────────────────
3.2  labor.alpha_routine
─────────────────────────────────────────────────────────────────────
  path:       labor.alpha_routine
  base:       +0.20  (+20% faster)
  hard_min:   -0.10
  hard_max:   +0.70
  mc_low:     +0.05
  mc_high:    +0.45
  confidence: LOW-MEDIUM
  source:     BIS field experiment (Gambacorta et al. 2024): ~25%
              productivity gain in controlled coding task.
              GitHub Copilot study (Kalliamvakou 2022): 55% faster
              on isolated HTTP server task.
              Weisz et al. 2025 surveys: 12-25% self-reported gains.
              None of these are RCTs; all use isolated or greenfield
              tasks where AI tools perform best.
  notes:      Applies once alpha_maturation_years has elapsed. This
              is the long-run steady-state productivity gain from
              routine automation. The wide range reflects genuine
              uncertainty: task type dominates the effect, and the
              proportion of engineering time on "routine" tasks varies
              enormously by role and codebase.

─────────────────────────────────────────────────────────────────────
3.3  labor.alpha_maturation_years
─────────────────────────────────────────────────────────────────────
  path:       labor.alpha_maturation_years
  base:       5.0  years
  hard_min:   1.0
  hard_max:   15.0
  mc_low:     2.0
  mc_high:    8.0
  confidence: LOW
  source:     Structural assumption with no direct empirical basis.
              Grounded in: (a) tools are improving rapidly,
              (b) METR finding may generalize 2-4 years, not forever,
              (c) engineers need time to develop new workflows.
  notes:      Controls how fast alpha shifts from alpha_experienced
              (METR drag) toward alpha_routine (routine gains).
              This is the third most impactful parameter for
              break-even year timing after g_tools and parkinson.
              If METR follow-up shows neutralization with 2026 tools,
              this should be revised to 2-3 years.
              Sensitivity: alpha_maturation_years=2 → break-even yr3;
                           alpha_maturation_years=8 → break-even yr8.

─────────────────────────────────────────────────────────────────────
3.4  labor.f_auto  (automatable task fraction)
─────────────────────────────────────────────────────────────────────
  path:       labor.f_auto
  base:       0.35  (35%)
  hard_min:   0.10
  hard_max:   0.75
  mc_low:     0.20
  mc_high:    0.55
  confidence: MEDIUM
  source:     Stack Overflow 2024 Developer Survey (N=65,437):
              developers spend ~30-40% of time writing code; rest is
              meetings, code review, debugging, architecture.
              McKinsey 2023: ~40% of developer activities are
              "highly automatable" by current AI.
              GitClear 2025: AI teams produce 8x more duplicated code,
              suggesting automatable code is being generated.
  notes:      Grows at 4%/yr in the model, capped at 70%.
              This captures the expanding scope of automation as
              tools cover more task types. Does NOT include cognitive
              tasks (those are in f_cognitive separately).
              The 70% cap reflects a structural floor of tasks
              requiring human judgment that cannot be automated.

─────────────────────────────────────────────────────────────────────
3.5  labor.f_verify  (verification overhead)
─────────────────────────────────────────────────────────────────────
  path:       labor.f_verify
  base:       0.25  (25% of automation benefit consumed by review)
  hard_min:   0.00
  hard_max:   0.70
  mc_low:     0.08
  mc_high:    0.50
  confidence: NONE
  source:     No direct empirical basis. CMU SEI 2024: AI-generated
              code introduces ~35% more technical debt, implying
              non-trivial review burden. METR slowdown partly
              attributed to verification time. Qualitative: 30-50%
              of AI code requires significant rework (practitioner
              reports). Cannot be precisely calibrated.
  notes:      Applied as: verification_drag = f_verify × f_auto_t
              × max(0, -alpha_experienced).
              Higher f_verify offsets more of the automation benefit.
              Wide mc range reflects fundamental uncertainty about
              how much review AI-generated code requires in practice.

─────────────────────────────────────────────────────────────────────
3.6  labor.g_tools  (annual tool improvement rate)
─────────────────────────────────────────────────────────────────────
  path:       labor.g_tools
  base:       0.20  (20% per year)
  hard_min:   0.00
  hard_max:   0.80
  mc_low:     0.08
  mc_high:    0.45
  confidence: NONE
  source:     No empirical basis. AI capability trajectory is
              genuinely unknown. 20%/yr is chosen as a middle estimate
              consistent with observable model release pace (GPT-3.5
              to Claude 3.5 to Opus 4 etc.) but this is not a
              calibrated measure of engineering productivity improvement.
  notes:      THE SINGLE MOST IMPACTFUL UNCERTAIN PARAMETER.
              Sensitivity: g_tools=0.10 → break-even never (within 10yr)
                           g_tools=0.20 → break-even yr5 (base)
                           g_tools=0.35 → break-even yr3
              Wide mc range is appropriate given genuine ignorance.
              Does not compound geometrically to unreasonable values
              because it is multiplied by adoption_fraction.

═══════════════════════════════════════════════════════════════════════
SECTION 4: COGNITIVE PARAMETERS (V5 — ALL NO EMPIRICAL BASIS)
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
4.1  cognitive.alpha_cognitive
─────────────────────────────────────────────────────────────────────
  path:       cognitive.alpha_cognitive
  base:       0.15  (15% gain on cognitive tasks when AI-assisted)
  hard_min:   0.00
  hard_max:   0.50
  mc_low:     0.00  (includes possibility of no cognitive benefit)
  mc_high:    0.30
  confidence: NONE
  source:     No empirical basis. Represents the productivity gain
              on architectural reasoning, debugging hypothesis
              generation, requirements formalization, and context
              synthesis when these are AI-assisted. Speculative.
  notes:      Setting to 0.0 = cognitive tools have no effect.
              Setting to 0.30 = strong cognitive assistance.
              Run scenario cognitive_off to exclude this entirely.
              mc_low = 0.00 because it is entirely plausible that
              current tools do not meaningfully assist cognitive work.

─────────────────────────────────────────────────────────────────────
4.2  cognitive.f_cognitive
─────────────────────────────────────────────────────────────────────
  path:       cognitive.f_cognitive
  base:       0.35  (35% of engineering time is cognitive tasks)
  hard_min:   0.10
  hard_max:   0.70
  mc_low:     0.20
  mc_high:    0.55
  confidence: NONE
  source:     Estimated from task time allocation studies (Stack
              Overflow, McKinsey). Senior engineers spend ~55-70%
              of time on cognitive work; juniors ~15%. Aggregate
              estimate ~35%. No direct measurement.
  notes:      Distinct from f_auto: cognitive tasks (architecture,
              debugging, requirements) are different from routine
              tasks (coding, testing, documentation). These overlap
              imperfectly; the model treats them as separate.

─────────────────────────────────────────────────────────────────────
4.3  cognitive.cognitive_scope_max
─────────────────────────────────────────────────────────────────────
  path:       cognitive.cognitive_scope_max
  base:       0.30  (30% ceiling)
  hard_min:   0.00
  hard_max:   0.80
  mc_low:     0.00
  mc_high:    0.55
  confidence: NONE
  source:     No empirical basis. Represents the maximum fraction of
              cognitive work that can ever become AI-assisted. 30%
              is conservative: some cognitive work (novel problem
              framing, stakeholder negotiation, value judgments)
              requires human judgment that cannot be outsourced.
  notes:      The ceiling that cognitive_scope grows toward.
              The mc range is very wide because this captures deep
              uncertainty about the ultimate scope of AI cognitive
              assistance. mc_low = 0.00 again includes no effect.

─────────────────────────────────────────────────────────────────────
4.4  cognitive.cognitive_growth_rate
─────────────────────────────────────────────────────────────────────
  path:       cognitive.cognitive_growth_rate
  base:       0.15  (15% per year toward ceiling)
  hard_min:   0.00
  hard_max:   0.60
  mc_low:     0.05
  mc_high:    0.35
  confidence: NONE
  source:     No empirical basis. Set slower than routine automation
              growth (g_tools) to reflect that cognitive tasks are
              harder problems for AI to assist with.
  notes:      Controls the saturation curve: cognitive_scope(t) =
              cognitive_scope_max × (1 - exp(-rate × t)).
              At 0.15/yr: cognitive scope reaches 53% of max by year5,
              78% of max by year10.

─────────────────────────────────────────────────────────────────────
4.5  cognitive.cognitive_maturation_years
─────────────────────────────────────────────────────────────────────
  path:       cognitive.cognitive_maturation_years
  base:       8.0  years
  hard_min:   2.0
  hard_max:   20.0
  mc_low:     4.0
  mc_high:    14.0
  confidence: NONE
  source:     No empirical basis. Set longer than alpha_maturation_years
              (5yr) to reflect that cognitive capability replication
              is harder than routine task automation. Judgment only.
  notes:      Controls how fast cognitive_alpha grows toward
              alpha_cognitive ceiling: cognitive_alpha(t) =
              alpha_cognitive × min(1, t/cognitive_maturation_years).

═══════════════════════════════════════════════════════════════════════
SECTION 5: DEMAND PARAMETERS
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
5.1  demand.price_elasticity (by segment)
─────────────────────────────────────────────────────────────────────
  paths:      demand.price_elasticity.consumer   base: 1.80
              demand.price_elasticity.smb         base: 1.40
              demand.price_elasticity.enterprise  base: 0.45
              demand.price_elasticity.regulated   base: 0.20
  hard_min:   0.00  (perfectly inelastic)
  hard_max:   4.00  (highly elastic)
  mc_low:     consumer=1.20, smb=0.80, enterprise=0.20, regulated=0.05
  mc_high:    consumer=2.50, smb=2.00, enterprise=0.80, regulated=0.40
  confidence: MEDIUM for enterprise/SMB; LOW for consumer/regulated
  source:     MCP Analytics 2025: "Enterprise clients may show -0.5
              elasticity while small businesses show -2.0."
              Guardrailed Elasticity Pricing (arXiv 2512.20932):
              Bayesian hierarchical elasticity across 2.3M SaaS
              subscription records.
              ResearchGate 2016: server markets "extremely inelastic."
  notes:      Price elasticity acts on annual price reduction, not
              cumulative price level. Enterprise SaaS is inelastic
              due to switching costs, long contracts, and compliance
              requirements. Consumer apps are elastic because
              freemium alternatives exist. Regulated industries
              near-zero because procurement/compliance dominates.

─────────────────────────────────────────────────────────────────────
5.2  demand.market_expandability (by segment)
─────────────────────────────────────────────────────────────────────
  paths:      consumer=0.60, smb=0.80, enterprise=0.30, regulated=0.20
  hard_min:   0.00  (fully saturated; price drop creates no new demand)
  hard_max:   1.00  (unlimited room to expand)
  mc_low:     consumer=0.35, smb=0.50, enterprise=0.15, regulated=0.10
  mc_high:    consumer=0.85, smb=0.95, enterprise=0.55, regulated=0.40
  confidence: LOW
  source:     Judgment. SMB has most room (many businesses still
              using spreadsheets over dedicated software). Enterprise
              software in large firms is fairly saturated. Regulated
              industries constrained by compliance rather than price.
  notes:      Multiplies the elasticity expansion. Acts as a ceiling
              on how much price-driven demand expansion can occur in
              each segment. Does not affect other demand components.

─────────────────────────────────────────────────────────────────────
5.3  demand.max_cumulative_expansion  (Baumol constraint)
─────────────────────────────────────────────────────────────────────
  path:       demand.max_cumulative_expansion
  base:       0.60  (elasticity can add at most 60% above baseline)
  hard_min:   0.05
  hard_max:   2.00
  mc_low:     0.20
  mc_high:    1.00
  confidence: NONE
  source:     No empirical basis. Reflects the Baumol constraint:
              as software gets cheaper, other inputs (PM, design,
              sales, customer success) become binding. Software
              market cannot expand indefinitely even if price falls
              toward zero. The 60% cap is conservative.
  notes:      Applied as a cumulative cap on price-elasticity demand
              only. Other demand components (backlog, underserved,
              induced) have their own ceilings.

─────────────────────────────────────────────────────────────────────
5.4  demand.backlog_initial_months
─────────────────────────────────────────────────────────────────────
  path:       demand.backlog_initial_months
  base:       6.0  months
  hard_min:   0.5
  hard_max:   24.0
  mc_low:     3.0
  mc_high:    12.0
  confidence: LOW
  source:     Proxy: Atlassian/LinearB: teams complete 65-70% of
              planned sprint work; 30-35% rolls over. Gartner 2023:
              average enterprise backlog is 6-18 months.
              Market average likely 4-8 months; 6 is central estimate.
  notes:      Firm model uses firm-specific backlog_months from
              profile. This is the market-level average. The demand
              signal from backlog is not the stock itself but the
              extra work completed vs. no-agentic baseline.

─────────────────────────────────────────────────────────────────────
5.5  demand.parkinson_coefficient
─────────────────────────────────────────────────────────────────────
  path:       demand.parkinson_coefficient
  base:       0.25  (25% of freed capacity becomes new scope)
  hard_min:   0.00  (no Parkinson: all freed capacity = savings)
  hard_max:   0.70  (strong Parkinson: most gains absorbed by scope)
  mc_low:     0.05
  mc_high:    0.50
  confidence: NONE
  source:     No empirical basis. Changed from 0.40 to 0.25 in v5
              after analysis showing 0.40 was making break-even too
              late and was hard to justify. 0.25 represents moderate
              scope expansion: one-quarter of every productivity gain
              turns into new work.
  notes:      THE SECOND MOST IMPACTFUL UNCERTAIN PARAMETER.
              Sensitivity: parkinson=0.10 → break-even yr4
                           parkinson=0.25 → break-even yr5 (base)
                           parkinson=0.45 → break-even yr8 or never
              Wide mc range reflects fundamental uncertainty about
              organizational behavior when capacity frees up.

─────────────────────────────────────────────────────────────────────
5.6  demand.agentic_expansion_rate
─────────────────────────────────────────────────────────────────────
  path:       demand.agentic_expansion_rate
  base:       0.10  (10% of adoption × B_initial per year)
  hard_min:   0.00
  hard_max:   0.40
  mc_low:     0.02
  mc_high:    0.25
  confidence: NONE
  source:     No empirical basis. Represents new projects entering
              the backlog because agentic tools make them feasible
              (projects that couldn't be built at old cost).
              Distinct from Parkinson (which fills existing capacity).
  notes:      Small contribution relative to Parkinson in the base
              case. Becomes more important if adoption is fast and
              tools enable genuinely novel project types.

─────────────────────────────────────────────────────────────────────
5.7  demand.tech_debt_initial_pct
─────────────────────────────────────────────────────────────────────
  path:       demand.tech_debt_initial_pct
  base:       40.0  (40% of engineering capacity on debt maintenance)
  hard_min:   5.0
  hard_max:   80.0
  mc_low:     25.0
  mc_high:    58.0
  confidence: HIGH — strongest empirical grounding in the model
  source:     McKinsey 2023: technical debt accounts for ~40% of
              IT balance sheets.
              Stack Overflow 2024 (N=65,437): 62% cite tech debt
              as #1 frustration.
              STX Next 2024: 91% of global CTOs name tech debt as
              biggest challenge.
              McKinsey survey of 50 CIOs: 60% saw tech debt increase.
  notes:      This is the demand model variable; firm model uses
              technical_debt_pct from the firm profile. The mc range
              is relatively tight given high empirical confidence.
              Lower values mean less refactoring demand; higher values
              mean more near-term demand but more maintenance drag.

─────────────────────────────────────────────────────────────────────
5.8  demand.ai_debt_premium
─────────────────────────────────────────────────────────────────────
  path:       demand.ai_debt_premium
  base:       0.35  (35% more debt per line for AI-generated code)
  hard_min:   0.00
  hard_max:   1.00
  mc_low:     0.10
  mc_high:    0.65
  confidence: MEDIUM
  source:     CMU SEI 2024: AI-generated code introduces ~35% more
              technical debt per line than human-written code.
              GitClear 2025: AI-assisted teams produce 8x more
              duplicated code, with refactored lines falling from
              25% (2021) to under 10% (2024) of all changes.
  notes:      Applied as: debt_inflow × (1 + premium × adoption).
              Higher premium means faster debt accumulation with
              agentic adoption, offsetting some of the productivity
              gain through increased maintenance burden. The 0.35
              CMU SEI figure has uncertainty because it was measured
              with specific tools and codebases.

─────────────────────────────────────────────────────────────────────
5.9  demand.underserved_fraction
─────────────────────────────────────────────────────────────────────
  path:       demand.underserved_fraction
  base:       0.25  (25% of current market size in underserved markets)
  hard_min:   0.00
  hard_max:   1.00
  mc_low:     0.05
  mc_high:    0.55
  confidence: NONE
  source:     No empirical basis. Proxy: ~40-60% of SMBs globally
              rely on spreadsheets rather than dedicated software.
              World Bank: 300M+ SMBs globally underserved. Cannot
              translate to engineering demand without assumptions
              about conversion rates and software complexity needed.
  notes:      Wide mc range appropriate. This is a large potential
              demand source (adds 6-7%/yr after activation) but
              has no calibration. Set to 0.0 for pessimistic
              scenarios where underserved markets don't materialize.

─────────────────────────────────────────────────────────────────────
5.10  demand.underserved_threshold
─────────────────────────────────────────────────────────────────────
  path:       demand.underserved_threshold
  base:       0.40  (40% cost reduction required to unlock)
  hard_min:   0.05
  hard_max:   0.80
  mc_low:     0.15
  mc_high:    0.65
  confidence: NONE
  source:     No empirical basis. Represents the minimum cost
              reduction required before underserved markets begin
              adopting software. Lower threshold = markets unlock
              sooner. At base 0.40 + 12%/yr cost reduction,
              activation begins around year 4-5.
  notes:      Interacts strongly with annual_cost_reduction_rate.
              If threshold=0.20 and cost_rate=0.12, markets activate
              in year 2-3 rather than year 4-5. Significant impact
              on timing of demand surge.

─────────────────────────────────────────────────────────────────────
5.11  demand.induced_market_size
─────────────────────────────────────────────────────────────────────
  path:       demand.induced_market_size
  base:       0.20  (new categories add up to 20% of current market)
  hard_min:   0.00
  hard_max:   1.00
  mc_low:     0.00
  mc_high:    0.45
  confidence: NONE
  source:     No empirical basis. Represents entirely new software
              categories created by agentic capabilities. Historical
              analog: internet created ~$4T software market that
              didn't exist before. But that was over 30 years; 20%
              in 10 years for agentic tools is already speculative.
  notes:      mc_low = 0.00 because entirely new categories may not
              materialize within the 10-year simulation horizon.

─────────────────────────────────────────────────────────────────────
5.12  demand.debt_productivity_drag
─────────────────────────────────────────────────────────────────────
  path:       demand.debt_productivity_drag
  base:       0.0003  (0.03% per percentage-point of debt)
  hard_min:   0.00
  hard_max:   0.005
  mc_low:     0.0001
  mc_high:    0.0010
  confidence: LOW
  source:     Rescaled in v4 from 0.003 (which produced 12%
              productivity drag — implausible). At 0.0003, 40% debt
              creates 1.2%/yr drag. Indirect support from
              maintenance cost studies; no direct measurement of
              debt impact on individual engineer productivity.
  notes:      Applied as: debt_drag = tech_debt_pct × drag_rate.
              Decreases as debt is paid down. Small absolute effect
              in base case (1.2% → 0.5% over 10yr) but non-zero.

═══════════════════════════════════════════════════════════════════════
SECTION 6: MARKET STRUCTURE
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
6.1  market.consumer_capture_rate (by segment)
─────────────────────────────────────────────────────────────────────
  paths:      consumer=0.70, smb=0.55, enterprise=0.30, regulated=0.20
  hard_min:   0.00  (firms keep all savings)
  hard_max:   1.00  (all savings passed to customers)
  mc_low:     consumer=0.35, smb=0.25, enterprise=0.10, regulated=0.05
  mc_high:    consumer=0.90, smb=0.80, enterprise=0.60, regulated=0.45
  confidence: LOW
  source:     General IO theory applied to software. Competitive
              markets pass through ~60-100% of cost reductions.
              Concentrated markets 0-30%. Software markets span
              this range: consumer apps are competitive; enterprise
              ERP is concentrated. No software-specific studies.
  notes:      Multiplies the elasticity demand signal. If capture_rate
              = 0 for all segments, price-elasticity demand = 0.
              This is the Incumbent Capture scenario. Most important
              for determining whether demand actually expands in
              response to falling costs.

─────────────────────────────────────────────────────────────────────
6.2  exogenous sub-components
─────────────────────────────────────────────────────────────────────
  paths:      exogenous.gdp_environment         base: 1.0
              exogenous.immigration_policy       base: 1.0
              exogenous.education_supply         base: 1.0
              exogenous.regulatory_environment   base: 1.0
  hard_min:   0.10  (extreme negative environment)
  hard_max:   2.50  (extreme positive environment)
  mc_low:     0.65 for all sub-components
  mc_high:    1.35 for all sub-components
  confidence: HIGH for GDP (IMF/World Bank data); NONE for others
  source:     GDP: IMF 2025 projections (global 3.2%, US 2.1%).
              Immigration: USCIS H-1B data; policy-dependent.
              Education: NCES CS graduation data (~3-5%/yr growth).
              Regulation: EU AI Act, US exec orders; labor effect unknown.
  notes:      Combined via weighted geometric mean into single
              exogenous_multiplier ∈ [0.5, 2.0]. Applied to net
              employment delta, not the level.

═══════════════════════════════════════════════════════════════════════
SECTION 7: FIRM MODEL VARIABLES
═══════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────
7.1  junior_fraction
─────────────────────────────────────────────────────────────────────
  field:      junior_fraction  (in FirmProfile)
  base:       0.35  (35%)
  hard_min:   0.05
  hard_max:   0.70
  mc_low:     0.20
  mc_high:    0.55
  confidence: LOW-MEDIUM
  source:     BLS occupational employment statistics; firm surveys.
              Startup teams often 40-50% junior. Large enterprise
              teams often 25-35% junior. Wide variation by industry.
  notes:      Drives junior displacement sensitivity. Higher junior
              fraction → larger headcount impact from junior
              displacement, but also more potential for cognitive
              leverage gap to widen.

─────────────────────────────────────────────────────────────────────
7.2  senior_fraction
─────────────────────────────────────────────────────────────────────
  field:      senior_fraction  (in FirmProfile)
  base:       0.20  (20%)
  hard_min:   0.05
  hard_max:   0.50
  mc_low:     0.12
  mc_high:    0.35
  confidence: LOW-MEDIUM
  source:     Industry surveys suggest 15-25% of engineers are
              senior/architect level at most firms.
  notes:      Combined with junior_fraction must be < 1.0.
              mid_fraction = 1 - junior - senior (implicit).

─────────────────────────────────────────────────────────────────────
7.3  revenue_growth_rate
─────────────────────────────────────────────────────────────────────
  field:      revenue_growth_rate  (in FirmProfile)
  base:       0.10  (10%)
  hard_min:   -0.20
  hard_max:   2.00
  mc_low:     0.02
  mc_high:    0.35
  confidence: HIGH for firm-specific historical data; LOW for forecast
  source:     Observable from firm financial data. Ranges:
              Government/regulated: 0-3%.
              Manufacturing/mature enterprise: 3-8%.
              Enterprise SaaS: 10-25%.
              High-growth consumer: 30-100%+.
  notes:      In the firm model, this rate decays toward
              long_run_growth_rate over time based on
              current_market_penetration. High initial rates are
              not sustained for the full 10-year horizon.

─────────────────────────────────────────────────────────────────────
7.4  current_market_penetration
─────────────────────────────────────────────────────────────────────
  field:      current_market_penetration  (in FirmProfile)
  base:       0.10  (10% of TAM captured)
  hard_min:   0.001
  hard_max:   0.90
  mc_low:     0.02
  mc_high:    0.50
  confidence: LOW (requires knowing TAM, which is ambiguous)
  source:     Observable in principle from market research data,
              but TAM definition is often contested. Ranges:
              Early-stage startup: 0.1-2%.
              Growth-stage: 2-15%.
              Mature product: 15-60%.
  notes:      Controls how fast revenue growth decays toward
              long_run_growth_rate. High penetration → fast decay.
              Low penetration → high growth can persist longer.
              Most important for EXPAND-strategy firms.

─────────────────────────────────────────────────────────────────────
7.5  backlog_months
─────────────────────────────────────────────────────────────────────
  field:      backlog_months  (in FirmProfile)
  base:       6.0  months
  hard_min:   0.0
  hard_max:   36.0
  mc_low:     2.0
  mc_high:    18.0
  confidence: LOW (proxy data; varies enormously by organization)
  source:     Gartner 2023: average enterprise backlog 6-18 months.
              LinearB/Atlassian: teams complete 65-70% of planned
              sprint work. High-growth startups often have 12-24
              months of backlog. Mature products may have 2-4 months.
  notes:      V5 fix: this is now the initial stock for FirmBacklogStock,
              which depletes as it is worked through and refills via
              firm_parkinson. Previously was a permanent static boost.
              The demand effect fades as backlog is cleared.

─────────────────────────────────────────────────────────────────────
7.6  technical_debt_pct
─────────────────────────────────────────────────────────────────────
  field:      technical_debt_pct  (in FirmProfile)
  base:       35.0  (35% of capacity on debt maintenance)
  hard_min:   0.0
  hard_max:   80.0
  mc_low:     15.0
  mc_high:    60.0
  confidence: HIGH for population average; MEDIUM for specific firm
  source:     McKinsey 2023: 40% average. Range: young codebases
              may be 10-20%; legacy enterprise systems 50-70%.
  notes:      Drives IMPROVE fork classification (>45% triggers
              IMPROVE signals). Also affects debt stock dynamics:
              higher initial debt → more near-term refactoring demand
              + more productivity drag.

─────────────────────────────────────────────────────────────────────
7.7  agentic_adoption_rate
─────────────────────────────────────────────────────────────────────
  field:      agentic_adoption_rate  (in FirmProfile)
  base:       0.30  (30% of engineers using mature agentic tools)
  hard_min:   0.00
  hard_max:   1.00
  mc_low:     0.05
  mc_high:    0.70
  confidence: LOW
  source:     Stack Overflow 2024: ~30% using AI tools regularly.
              But "mature agentic" is a higher bar than basic
              autocomplete. Startup engineers: 50-80%. Regulated
              industry: 5-20%.
  notes:      Ramps up over time in the model (+7%/yr, capped at
              1.0 × maturity_factor). Affects both the productivity
              gain the firm realizes and the debt accumulation rate.

─────────────────────────────────────────────────────────────────────
7.8  firm_parkinson_override / industry Parkinson coefficient
─────────────────────────────────────────────────────────────────────
  field:      firm_parkinson_override  (in FirmProfile, optional)
  industry defaults:
    consumer_tech:   0.45
    enterprise_saas: 0.30
    fintech:         0.20
    healthcare:      0.15
    manufacturing:   0.15
    government:      0.10
  hard_min:   0.00
  hard_max:   0.80
  mc_low:     0.05  (for specific firm)
  mc_high:    0.60  (for specific firm)
  confidence: NONE
  source:     No empirical basis. Industry defaults are judgment
              calls based on organizational culture: consumer tech
              product managers fill capacity immediately; government
              procurement constrains scope expansion.
  notes:      This is the firm-level Parkinson coefficient, distinct
              from the market-level demand.parkinson_coefficient.
              Controls how fast the firm's backlog refills after
              being cleared. Higher → backlog demand persists longer
              → headcount pressure from EXPAND sustained.

═══════════════════════════════════════════════════════════════════════
SECTION 8: PARAMETERS NOT VARIED IN MONTE CARLO
═══════════════════════════════════════════════════════════════════════

These parameters are fixed in Monte Carlo runs because they are design
choices or have hard structural constraints:

  simulation_years: 10           Design choice; not uncertain
  demand_ceiling: 3.0            Hard architectural bound
  backlog_floor_months: 2.0      Structural floor; not uncertain
  debt_floor_fraction: 0.15      Structural floor; not uncertain
  induced_start_year: 3          Design choice; not uncertain
  backlog_inflow_rate: 1.0       Normalized at 1.0 by definition
  backlog_completion_rate: 2.0   Calibrated to initial backlog level
  segment weights                Constrained to sum to 1.0
  pipeline_lag_years: 7          Structural; not in MC loop
  adoption_maturity (firm)       Categorical; set from profile
  industry (firm)                Categorical; determines fork biases
  will_pass_savings_to_customers Boolean; set from profile
  competitive_intensity          Categorical; set from profile
  software_is_core_product       Boolean; set from profile

═══════════════════════════════════════════════════════════════════════
SECTION 9: SUMMARY — PARAMETERS BY IMPORTANCE AND CONFIDENCE
═══════════════════════════════════════════════════════════════════════

Ranked by estimated impact on break-even year (most to least):

  Rank  Parameter                        Impact   Confidence
  ────  ─────────────────────────────────────────────────────
  1     labor.g_tools                    VERY HIGH  NONE
  2     demand.parkinson_coefficient     VERY HIGH  NONE
  3     labor.alpha_maturation_years     HIGH       LOW
  4     adoption.q                       HIGH       LOW
  5     context.annual_cost_reduction    HIGH       NONE
  6     labor.alpha_experienced          HIGH       MEDIUM
  7     demand.underserved_fraction      MEDIUM     NONE
  8     demand.tech_debt_initial_pct     MEDIUM     HIGH
  9     labor.f_verify                   MEDIUM     NONE
  10    market.consumer_capture_rate     MEDIUM     LOW
  11    cognitive.cognitive_scope_max    MEDIUM     NONE
  12    labor.alpha_routine              MEDIUM     LOW-MEDIUM
  13    demand.underserved_threshold     MEDIUM     NONE
  14    demand.ai_debt_premium           LOW-MED    MEDIUM
  15    production.phi                   LOW-MED    NONE
  16    cognitive.alpha_cognitive        LOW        NONE
  17    adoption.p                       LOW        LOW
  18    demand.induced_market_size       LOW        NONE
  19    demand.max_cumulative_expansion  LOW        NONE
  20    demand.debt_productivity_drag    VERY LOW   LOW
