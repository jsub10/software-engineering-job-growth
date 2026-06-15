# V5: Cognitive Capability Additions

## What Changed and Why

V4 modeled agentic coding as automating a fixed fraction of engineering *tasks*
(routine code, testing, documentation). This is the right model for task-substitution
tools like early Copilot.

It is the wrong model for cognitive tools that replicate human reasoning.

Agentic tools are beginning to assist with four cognitive capabilities that the
previous model treated as permanently human:

  1. SPECIFICATION AND DECOMPOSITION
     Breaking a problem into solvable pieces; proposing architectural approaches;
     identifying dependencies before writing any code. Engineers spend substantial
     time on this before touching a keyboard. When AI can propose a credible
     decomposition in minutes, engineers evaluate rather than generate — a large
     cognitive compression.

  2. CONTEXT SYNTHESIS ACROSS LARGE CODEBASES
     Understanding existing code before changing it. Reading, tracing, building
     a mental model of where things fit. Agentic tools with large context windows
     can do this synthesis faster than humans. Distinct from code generation.

  3. DEBUGGING HYPOTHESIS GENERATION
     Generating hypotheses about what could be wrong, designing tests to distinguish
     between them, interpreting results. Not routine. But agentic tools are
     surprisingly good at this for known bug categories, and improving rapidly.

  4. REQUIREMENTS ELICITATION AND FORMALIZATION
     Turning vague business needs into precise specifications, identifying
     ambiguities, proposing edge cases. Historically treated as fully human.
     Already partially automatable; will become more so.

## Three Additions to the Model

### 1. Three-Component Alpha (replaces two-component blend)

V4 blended two alpha values:
  alpha_experienced (-0.19, METR RCT): effect on experienced devs, mature codebases
  alpha_routine (+0.20, BIS/Copilot): effect on routine/isolated tasks

V5 adds a third:
  alpha_cognitive: effect on cognitive tasks (architecture, debugging, requirements)

  alpha_cognitive starts near 0.0 (tools are poor at this today)
  alpha_cognitive grows toward a ceiling (alpha_cognitive_ceiling) over time
  Growth follows its own maturation curve (slower than routine alpha)
  alpha_cognitive applies to a separate cognitive task fraction (f_cognitive)

  Empirical basis for alpha_cognitive: NONE
  This is the most speculative addition in the model.
  It must be treated as an assumption, not a calibration.
  It is explicitly parameterized and can be set to 0 to reproduce v4 behavior.

### 2. Cognitive Scope Expansion Term

V4: productivity growth is bounded by f_auto (automatable task fraction)
  Eventually saturates at ~70% of tasks, growing at 4%/year

V5: adds cognitive_scope_expansion
  Represents the expanding fraction of cognitive work that becomes AI-assisted
  Not the same as f_auto — these are qualitatively different tasks
  Has a lower floor (some cognitive work always requires human judgment)
  Has a slower growth rate than routine automation (harder problems take longer)
  Has a different ceiling (cognitive work is harder to fully automate)

  cognitive_scope(t) = cognitive_scope_max × (1 - exp(-cognitive_growth_rate × t))

  Default: cognitive_scope_max = 0.30, cognitive_growth_rate = 0.15
  Meaning: cognitive assistance eventually covers 30% of what is currently
  pure human cognitive work, growing at 15%/year of remaining headroom.

  Empirical basis: NONE. Highly speculative.

### 3. Cognitive Leverage in Firm Model

V4 applied uniform productivity gains across tiers (with simple tier modifiers).

V5 distinguishes cognitive leverage:
  Senior engineers / architects spend MORE time on cognitive tasks (spec, architecture,
  debugging complex systems). Cognitive tools therefore give them MORE leverage.

  A senior architect who previously spent 70% of time on cognitive work (architecture,
  debugging, requirements) and 30% on execution now has the cognitive work partially
  compressed. This frees time to pursue more ambitious projects, not just do the
  same projects faster.

  cognitive_leverage_factor(tier):
    architect: 1.6  (70% cognitive work, highest leverage)
    senior:    1.4  (55% cognitive work)
    mid:       1.1  (35% cognitive work)
    junior:    0.7  (15% cognitive work, REDUCED leverage — cognitive tools less useful
                    when you don't yet know what to think about)

  The junior factor < 1.0 is important: cognitive tools require knowing what question
  to ask, what to specify, what constitutes a good architectural approach.
  Junior engineers benefit LESS from cognitive tools than from routine automation tools,
  because they lack the domain knowledge to direct the cognitive AI effectively.
  This is a key v5 prediction: the skill pyramid compresses at the top and expands
  the gap at the bottom.

## Empirical Confidence

  alpha_cognitive:          NONE — no studies; highly speculative
  cognitive_scope_max:      NONE — no studies
  cognitive_growth_rate:    NONE — no studies
  cognitive_leverage_factor: LOW — derived from task-time allocation studies,
                             but the translation to leverage is assumed

  The three additions are all in the LOW-NONE confidence tier.
  They are explicitly parameterizable and default to conservative values.
  Setting alpha_cognitive=0, cognitive_scope_max=0 reproduces v4 exactly.

## What Changes in the Model's Predictions

Adding cognitive capabilities changes the model in two directions:

  1. PRODUCTIVITY GROWS FASTER AND TO A HIGHER CEILING
     Because cognitive tasks (architecture, debugging, requirements) represent
     30-50% of senior engineer time, and cognitive tools compress this, net
     productivity gains are larger and less bounded than v4 suggested.

  2. THE SKILL PYRAMID BECOMES MORE SKEWED
     Senior engineers gain MORE leverage (cognitive work is compressed).
     Junior engineers gain LESS leverage (cognitive tools require expertise to direct).
     The gap between junior and senior productivity — and therefore the demand for
     senior vs. junior roles — widens more than v4 predicted.

  These two effects have opposing implications for Jevons:
    More productivity → harder for demand to keep up → Jevons more likely to fail
    But more leverage per senior engineer → firms can pursue more ambitious projects
    → demand expands in a way that is qualitatively different from task automation

  The model cannot resolve which effect dominates because alpha_cognitive has no
  empirical calibration. But it can show the SHAPE of the difference:
  with cognitive capabilities, the outcome is more extreme in both directions —
  either substantially more engineers (if cognitive leverage drives demand expansion)
  or substantially fewer (if cognitive productivity dominates and demand doesn't expand).
