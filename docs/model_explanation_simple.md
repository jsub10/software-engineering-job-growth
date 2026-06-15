# Will Agentic Coding Increase or Decrease the Number of Software Engineers?
## A Plain-Language Guide to the Model

---

### The Central Question

Agentic coding tools — AI systems that can write, test, and deploy software with minimal
human direction — are making software engineers dramatically more productive. When a
technology makes workers more productive, one of two things happens:

**More output, same workers:** The productivity gain gets reinvested in building more
software. Employment stays flat or grows because there was always more software
to build than engineers to build it.

**Same output, fewer workers:** The productivity gain gets harvested as cost reduction.
Fewer engineers produce the same software as before. Employment falls.

Which one happens for software engineering is the central question this model tries
to answer.

---

### The Short Answer

We genuinely do not know — and anyone who tells you confidently is probably wrong.

What we can say is:

- **In the near term (years 1-3):** demand likely grows faster than productivity.
  There is a large existing backlog of work that suddenly becomes viable, and tools
  take time to reach most engineers. Jevons holds: more software gets built,
  employment stays flat or grows slightly.

- **In the medium term (years 4-7):** it depends on two things we cannot measure:
  how fast agentic tools improve, and what fraction of firms decide to harvest
  versus reinvest the efficiency gain.

- **In the long term (years 8-10):** productivity growth from tools is likely to
  outpace demand growth unless new software categories emerge at scale.
  Employment probably falls unless new markets open.

The most important insight: **the near term looks better for engineers than the long term.**

---

### Why We Can't Just Say "More Productive = Fewer Jobs"

The naive view is: if each engineer can do twice the work, you need half as many
engineers. But this has been wrong repeatedly in history.

**ATMs were supposed to eliminate bank tellers.** Instead, because each branch cost
less to staff, banks opened more branches. Total teller employment went up.

**Spreadsheets were supposed to eliminate accountants.** Instead, spreadsheets made
financial analysis faster and cheaper, so organizations did far more of it. Accountant
employment went up.

**CAD software was supposed to eliminate engineering draftspeople.** Instead, it made
iteration cheaper, so engineers designed more complex products. Employment went up.

**Word processors eliminated typists and secretaries.** Managers started typing
their own documents. Employment went down sharply.

What determined the outcome was whether the productivity gain opened up new demand —
new things to build that weren't feasible before — or just made the existing thing
cheaper. Software engineering looks much more like CAD and spreadsheets than like
word processing, for a specific reason: there has always been far more software
worth building than engineers available to build it.

---

### The Three Things That Determine the Outcome

**1. How fast do the tools actually improve?**

This is what we know least about. Current evidence is mixed: a rigorous randomized
controlled trial (METR, July 2025) found that experienced developers were actually
19% *slower* with early 2025 AI tools on complex, mature codebases. But developers
on simple, new projects report 20-55% speedups. The tools are improving rapidly
and the picture will look different in 2-3 years.

The model does not know how fast tools will improve. What it tells you is:
if tools improve faster than X% per year, employment falls. If slower, it rises.
That threshold — X — is the model's most useful output.

**2. How much of the efficiency gain gets passed to the market vs. kept as profit?**

If software companies use agentic tools to produce the same products at lower cost
and pocket the difference as margin, demand for software does not grow. Fewer
engineers are needed.

If they pass the savings to customers through lower prices or more features,
software demand grows because new buyers can now afford it, or existing buyers
buy more. More engineers are needed.

This is the most important variable in the model and the one with no good data.
It depends on competitive dynamics, management philosophy, and capital markets
pressure in ways that vary enormously by firm and industry.

**3. What does each individual firm decide to do?**

The model calls this the "management fork." When your engineers become more
productive, your firm faces a choice:

- **Harvest:** Take the productivity gain as cost savings. Reduce headcount over time.
  *Who does this: firms where software is a cost center, not a product; low competition;
  pressure to improve margins.*

- **Reinvest:** Keep headcount flat, produce more and better software with the same team.
  *Who does this: firms where software is the product but competitive pressure is moderate;
  want quality improvements.*

- **Expand:** Hire more engineers because you now have more projects that are viable at
  lower cost. Use productivity gain to grow.
  *Who does this: high-growth firms, strong competition, large backlog of work waiting.*

- **Improve:** Use the productivity gain to fix things that have been deferred — technical
  debt, refactoring, quality. Headcount stays flat. This is different from Reinvest
  because output quantity doesn't grow; output quality does.
  *Who does this: regulated industries, firms with high technical debt, mature products.*

Most firms will do some mix. But the primary strategy matters enormously: two firms
with identical engineers and identical tools will have very different headcount
trajectories based on which fork they choose.

---

### Three Things the Model Gets Right That Simpler Analyses Miss

**1. Backlog and technical debt never go to zero — and they keep accumulating.**

The near-term employment boost from agentic coding partly comes from clearing the
enormous backlog of work that software teams have. But backlog doesn't just get
cleared — it also grows. As teams ship faster, product managers ask for more.
As new possibilities open up, new projects get added. And AI-generated code actually
creates *more* technical debt per line than human-written code, because it tends
to produce more copy-paste code and less well-structured code.

This means the demand surge from clearing backlog is real but smaller than a naive
model suggests, and it doesn't last as long. The ongoing demand from new backlog
accumulation is more persistent but grows more slowly.

**2. Markets saturate.**

Agentic coding will not cause software to consume 100% of economic activity. At some
point, every potential customer has been served, every useful software product has
been built, and the marginal return on new software falls. The model explicitly caps
demand at plausible maximum levels — something that prior versions did not do.

**3. Junior engineers are the most exposed, but the pipeline matters.**

Agentic tools are most effective at the kinds of tasks junior engineers do: routine
code, documentation, testing, debugging simple bugs. This is already showing up in
data — entry-level software job postings have fallen 28% from their 2022 peak.

But if junior roles disappear, where do senior engineers come from in 10 years?
Senior engineers develop through years of doing junior work. If that pathway is cut,
there will be a shortage of senior engineers around 2030-2033 even if overall
headcount appears stable today. The model tracks this pipeline effect with a lag.

---

### What to Watch to Know Which Way This Goes

The model identifies four things that will determine whether engineer employment
rises or falls over the next decade. Track these:

**Watch the METR study.** The nonprofit METR is running randomized controlled trials
measuring actual AI productivity effects on experienced developers. Their early-2025
study found a 19% slowdown. Their late-2025 study (using newer tools) is ongoing.
If the updated study shows strong productivity gains, the break-even threshold shifts
dramatically and Jevons becomes much harder to sustain.

**Watch enterprise software pricing.** If major enterprise software companies
(Salesforce, SAP, ServiceNow, Workday) start cutting prices as their development
costs fall, it means savings are being passed to the market — a positive sign for
employment. If their margins expand without price reductions, savings are being
harvested.

**Watch entry-level hiring at large tech firms.** The 28% decline in entry-level
postings is a leading indicator of both short-term displacement and long-term
pipeline damage. If it reverses, Jevons is winning. If it continues declining,
the profession is restructuring away from junior roles.

**Watch the size of software backlogs.** If firms report that their software
backlogs are growing despite using AI tools (Parkinson's Law in action), demand
is expanding to fill capacity and Jevons holds. If firms report completing their
backlog and having nothing left to build, demand has saturated and employment will fall.

---

### The Bottom Line

Agentic coding will almost certainly change *who* software engineers are and *what
they do* more than it will change *how many* there are — at least in the next
five years.

Junior and routine coding roles face the highest displacement risk. Senior roles
involving architecture, requirements, oversight of AI systems, and complex judgment
face the lowest risk and may see increasing demand.

Whether total headcount rises, falls, or stays flat over the decade depends on
whether the demand expansion effect (more software gets built because it's cheaper)
outpaces the productivity effect (each engineer produces more software). History
suggests demand expansion wins more often than not when the technology opens up
genuinely new possibilities. Agentic coding meets that test — but saturation,
market limits, and management decisions about how to deploy efficiency gains will
determine the actual outcome.

The honest answer is: we will know more in 18-24 months than we do today,
and the METR productivity studies and enterprise pricing trends will be the
earliest reliable signals.

---

### A Note on Model Limitations

This model is a thinking tool, not a prediction. It forces assumptions to be made
explicit and shows how different assumptions lead to different conclusions. It should
not be used to produce precise headcount forecasts. It should be used to:

- Understand which variables matter most
- Identify what to watch as leading indicators
- Think through how a specific firm's characteristics affect its likely trajectory
- Stress-test intuitions about AI and employment by making the reasoning explicit

The nine parameters in the model with no empirical basis are explicitly flagged.
Any scenario that hinges primarily on those parameters should be treated as
illustrative, not predictive.
