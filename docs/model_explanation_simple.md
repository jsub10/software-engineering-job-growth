# Will Agentic Coding Increase or Decrease the Number of Software Engineers?
## A Plain-Language Guide to the Model (v5)

---

### The Central Question

Agentic coding tools — AI systems that can write, test, debug, and deploy software
with minimal human direction — are making software engineers more productive.
When a technology makes workers more productive, one of two things historically happens:

  MORE OUTPUT, SAME WORKERS: the productivity gain gets reinvested in building
  more software. Employment stays flat or grows because there was always more
  software worth building than engineers to build it.

  SAME OUTPUT, FEWER WORKERS: the productivity gain gets harvested as cost
  reduction. Fewer engineers produce the same software as before. Employment falls.

Which happens for software engineering? This model tries to answer that question.

---

### The Short Answer

We genuinely do not know. The model's base case says:

  Engineers peak at about 11% above baseline by year 4.
  Employment starts declining in year 5.
  By year 5 (the end of the modeled horizon), still about 11% above baseline.

But this single trajectory hides a very wide range of plausible outcomes.
The two parameters that matter most — how fast AI tools improve and how much
freed engineering capacity gets immediately filled with new work — have no
empirical calibration. Depending on those two parameters, the break-even year
(when employment starts declining from its peak) ranges from year 3 to "never
within the simulation horizon." The model is honest about this range rather
than hiding it in a single number.

---

### What the Model Actually Predicts

The model outputs three numbers that together tell the story better than any
single employment index:

  PEAK EMPLOYMENT — how high above baseline engineers get before the decline.
  BREAK-EVEN YEAR — when employment peaks and starts declining.
  FINAL EMPLOYMENT — where employment lands in the final year of the horizon.

The break-even year is the most useful of the three because it answers a
practical question: how long does the window of rising engineering employment
last before productivity gains outpace demand growth?

Under base assumptions (year 5 break-even), this window is about four years.
If tools improve faster than assumed, it shrinks to two or three years.
If demand is more elastic than assumed, employment may not decline within the
horizon at all.

---

### Why the Answer Isn't Simply "More Productive = Fewer Jobs"

The naive view is: if each engineer can do twice the work, you need half as many.
This has been wrong repeatedly in the history of productivity-enhancing technology.

ATMs were supposed to eliminate bank tellers. Instead, because each branch cost
less to staff, banks opened more branches. Total teller employment went up.

Spreadsheets were supposed to eliminate accountants. Instead, spreadsheets made
financial analysis faster and cheaper, so organizations did far more of it.
Employment went up.

CAD software was supposed to eliminate engineering draftspeople. Instead it made
iteration cheaper, so engineers designed more complex products. Employment went up.

Word processors eliminated typists and secretaries. Managers started typing their
own documents. Employment fell sharply.

What determined the outcome was whether the productivity gain opened up new
demand — new things to build that weren't feasible before — or just made the
existing thing cheaper to produce. Software engineering looks much more like
CAD and spreadsheets than word processing, because there has always been far
more software worth building than engineers available to build it.

---

### The Demand Side: Why Employment Rises Before It Falls

In the first few years, several demand forces work together to keep employment
above baseline even as productivity rises:

  BACKLOG CLEARANCE: Every software organization has a backlog of work that
  couldn't be done before because capacity was the bottleneck. When productivity
  rises, this backlog starts getting cleared — creating real demand for
  engineering work that wasn't being met before. This is front-loaded: it
  creates the biggest demand boost in the first two to four years.

  TECHNICAL DEBT: About 40% of engineering capacity in a typical organization
  goes to maintaining and working around legacy code rather than building new
  things. As AI tools make refactoring cheaper, organizations begin addressing
  debt they've deferred for years. This is also front-loaded but creates
  meaningful demand for a few years.

  UNDERSERVED MARKETS: Many sectors have been too expensive to serve with
  custom software — small businesses, agriculture, local government, nonprofits.
  As software gets cheaper to build, these markets begin to open. This demand
  activates later (around year 4-5 in the base case) and then slowly depletes
  as the market gets served.

All three of these demand forces eventually exhaust themselves. The backlog
gets cleared. The debt gets addressed. The underserved markets get served.
Meanwhile, productivity keeps growing as more engineers adopt tools and
tools keep improving. That's why employment eventually peaks and starts falling.

---

### Parkinson's Law and Why Employment Stays High Longer Than You'd Expect

There's a counterweight to the demand exhaustion: organizations tend to fill
available capacity with new work. When your engineering team gets 20% more
productive, product managers tend to ask for 20% more features. This is
Parkinson's Law applied to software development.

The model captures this through a "Parkinson coefficient" — a measure of how
much freed capacity gets immediately filled with new scope. At the base setting
(25%), one-quarter of every productivity gain becomes new work rather than
cost savings. This is why the backlog keeps refilling even as it gets cleared,
and why demand stays elevated longer than a simple one-time-release model
would suggest.

Parkinson's Law is real — anyone who has managed an engineering team knows
that faster engineers get asked to do more. But it has limits. Organizations
don't have infinite valuable projects to build. Eventually, strategic priorities
cap how much new scope gets approved, and the Parkinson effect weakens.

---

### The New Thing in This Version: Cognitive Capability Replication

Previous versions of this model treated AI as automating a fixed fraction of
engineering tasks — routine coding, testing, documentation. This is the right
model for autocomplete-style tools.

Agentic tools are beginning to do something qualitatively different: they are
beginning to replicate aspects of how engineers *think*, not just what engineers *type*.

Specifically, they are beginning to assist with:

  ARCHITECTURAL REASONING: breaking a problem into solvable pieces, identifying
  dependencies, proposing implementation approaches. Engineers spend significant
  time here before writing any code. When AI can propose a credible decomposition
  in minutes, engineers evaluate rather than generate.

  CODEBASE CONTEXT SYNTHESIS: understanding a large existing codebase before
  changing it. Engineers read and trace code for hours before making a change.
  AI can do this synthesis much faster.

  DEBUGGING HYPOTHESIS GENERATION: reasoning about what could be wrong, designing
  tests to distinguish between hypotheses. Not routine. But AI is surprisingly
  good at this for known bug patterns.

  REQUIREMENTS FORMALIZATION: turning vague business needs into precise technical
  specifications. This has always been considered fully human. It's becoming
  partially AI-assisted.

This cognitive assistance changes the productivity story in two ways:

First, productivity grows faster and to a higher ceiling than pure task
automation would predict. This means employment peaks sooner and falls
faster than the base model (before adding cognitive tools) suggests.

Second — and this is the important distributional effect — cognitive tools are
*not equally useful* to all engineers.

A senior engineer or architect who spends 60-70% of their time on architectural
reasoning, complex debugging, and specification can get enormous leverage from
cognitive tools. Their judgment is amplified.

A junior engineer who spends most of their time on routine coding — and who
doesn't yet have the domain expertise to know what architectural question to
ask — gets less benefit from cognitive tools than from routine automation tools.
You need to know what you're looking for before AI can help you find it.

The model therefore predicts that cognitive tools widen the productivity gap
between senior and junior engineers. Under the optimistic cognitive scenario,
senior employment is around 44% above baseline while junior employment is around
20% below baseline by the final year. The profession polarizes.

---

### What Determines Which Way This Goes

There are three things to watch that will tell you whether the break-even
year arrives early (around year 3) or not within the horizon at all:

  1. HOW FAST TOOLS ACTUALLY IMPROVE
     The model runs on a 20%/yr tool improvement rate. This is the most
     impactful uncalibrated number in the entire model. At 10%/yr,
     employment keeps rising throughout the horizon. At 35%/yr, employment
     starts falling by year 3. The METR randomized controlled trial
     (July 2025) found tools actually *slowed* experienced developers by 19%
     on complex mature codebases in early 2025. But tools have improved since
     then, and METR is running a follow-up. That study will be the most
     informative empirical signal available.

  2. HOW STRONG PARKINSON'S LAW IS
     If freed capacity immediately refills with new scope (strong Parkinson),
     demand stays elevated and break-even arrives later. If organizations
     actually harvest the efficiency gains rather than expanding scope, demand
     falls quickly and break-even arrives sooner. The model's cross-plot
     (run: python run.py --crossplot) shows break-even ranging from year 3
     to "never" depending on these two parameters alone.

  3. WHAT MANAGEMENT DECIDES TO DO WITH EFFICIENCY GAINS
     This is the pivotal question the model cannot answer from observable data.
     When your engineers become more productive, do you reduce headcount
     (harvest), keep the same team and build more (reinvest), hire more
     because new projects are now viable (expand), or use the gains to fix
     the code quality backlog (improve)? This decision varies enormously by
     firm, competitive environment, and management philosophy. The firm model
     classifies each firm into one of these four strategies based on observable
     characteristics, but the actual choice depends on factors the model cannot
     see.

---

### What Individual Firms Should Expect

The model's firm-level forecasts reflect four very different trajectories
depending on management strategy:

  HARVEST FIRMS (government IT, manufacturing IT, cost-center software):
  Headcount likely falls 10-30% over the simulation horizon as productivity
  gains are captured as cost reduction. The backlog gets cleared but not refilled.
  Low competitive pressure means there's no urgency to reinvest.

  REINVEST FIRMS (enterprise SaaS, mid-market tech):
  Headcount stays roughly flat. Engineers produce more software with the same
  team. Revenue grows; margins improve. Senior roles grow slightly; junior
  roles shrink. Technical debt gets addressed.

  EXPAND FIRMS (consumer tech, high-growth startups):
  Headcount grows significantly early as the large backlog gets cleared and
  new projects become viable. Growth moderates as backlog depletes and revenue
  growth decelerates toward long-run rates. The absorption cap (35%/yr maximum
  hiring pace) prevents unrealistic explosive growth.

  IMPROVE FIRMS (regulated industries, high-debt legacy systems):
  Headcount flat. Engineering productivity gains absorbed into quality
  improvement, compliance work, and technical debt reduction. The codebase
  gets better but headcount doesn't change much. This is actually a common
  outcome that simple models miss entirely.

The firm's current backlog is important early but not indefinitely. As AI tools
clear the backlog, new scope refills at a rate that depends on the organization's
culture and management approach — much faster at startups (where product managers
immediately request more features) than at government agencies (where procurement
limits scope expansion). The model now correctly models this depletion, rather
than treating the backlog as a permanent demand boost.

---

### What This Model Cannot Tell You

This model is honest about its limits:

  It cannot forecast aggregate employment with precision. Too many key
  parameters have no empirical basis. Treat it as a structured way of
  thinking about the problem, not as a prediction.

  It cannot model the transition path. The model shows where employment
  will be in equilibrium, not how it gets there. Hiring lags, reskilling
  time, and organizational inertia all matter in practice and are not
  captured.

  It cannot tell you which fork a specific firm will take. That depends
  on management intent, which is not derivable from observable characteristics.
  The fork classification is a hypothesis, not a measurement.

  The cognitive component is entirely speculative. The V5 additions for
  cognitive capability replication have no empirical basis. They represent
  a structural hypothesis about where tools are heading, not a calibrated
  estimate of where they are now. Run the model without cognitive tools
  (scenario: cognitive_off) to see how much the cognitive assumption matters.

---

### The Most Honest Bottom Line

Agentic coding will almost certainly change *who* software engineers are
and *what they do* more than it changes *how many* there are — at least
in the next five years.

The near term is better for engineers than the long term. Employment rises
before it falls, because demand forces (backlog clearance, debt remediation,
newly viable markets) front-load positive effects while productivity growth
starts slow due to low adoption and the METR-documented drag on experienced
developers in complex codebases.

The skill premium for senior engineers is growing, not shrinking. Cognitive
tools amplify expertise. The engineers who know what architectural question
to ask are getting more leverage, not less. The engineers doing routine
work face more displacement.

The fundamental uncertainty is whether the demand expansion from newly viable
software (smarter products, newly affordable markets, qualitatively new
categories) outpaces the productivity growth from tools. History suggests
it often does — CAD, spreadsheets, and ATMs all created more jobs than they
displaced. But word processors show it doesn't always. The difference is
whether the technology opens up new things to do or just does the old things
faster. The current evidence suggests agentic tools do both, making the
outcome genuinely ambiguous.

We will know substantially more in 18-24 months. The METR productivity
study update, enterprise software pricing trends, and entry-level hiring
patterns at large tech firms will be the earliest reliable signals of which
way this is going.
