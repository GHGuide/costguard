# CostGuard — Phase-2 presentation script

Spoken script for the live finale. ~2 minutes total. One thought per slide, plain
delivery, no reading the slide out loud. Numbers are all real (BRIEF.md + the
verified live runs).

---

**Slide 1 — Cover (~8s)**
> CostGuard. A cost-regression test for AI agents, built and run on UiPath.

**Slide 2 — Builder (~5s)**
> Built solo, for Track 3 — Test Cloud. Here's the one idea.

**Slide 3 — Problem & Solution (~30s)**
> Teams ship AI agents fast, and a small prompt or model change can quietly triple the bill while still passing every correctness test. We test whether an agent is *right*. We never test what it costs to be right.
> CostGuard is the missing gate. Before a change ships, it runs the agent many times, prices each correct outcome, compares it to the last approved version, and blocks a cost regression — with a human owning the call. The line nobody else can draw is cost per business outcome. That's the attribution problem FinOps flagged as unsolved.

**Slide 4 — Benefits & technologies (~25s)**
> Who's it for: platform, QA, and FinOps teams shipping agents to production. In our demo a "smarter" candidate gained four percent accuracy but cost seven times more per invoice — CostGuard blocked it. It runs on Test Cloud, coded agents, Orchestrator, Action Center, and Document Understanding, and it gates external LangChain agents the same way.

**Slide 5 — Architecture (~20s)**
> The flow is simple. A change goes in. The agent runs many times on UiPath. We price each correct outcome, compare to the baseline, and route any block to a human in Action Center. Every box on this diagram is a UiPath component.

**Slide 6 — Live proof (~25s)**
> And it's real, not a slide. A live serverless job on UiPath returned FAIL — seven times the cost for four percent accuracy. On real gateway models, the same upgrade cost thirteen times for zero gain. The verdict is registered as a first-class Test Cloud result, and the gate itself scores thirty out of thirty on a labelled eval.

**Slide 7 — Closing (~8s)**
> Looked fine. Cost seven times more. Blocked before it shipped. That's CostGuard.

---

**Q&A anticipation**
- *"Isn't this FinOps, not testing?"* → It's a test type: it runs in Test Cloud, returns a pass/fail verdict, and gates promotion. FinOps reports after the fact; CostGuard blocks before.
- *"How do you handle non-determinism?"* → N runs with a bootstrap confidence interval, not a single run. It only fails when the candidate's interval clears the baseline's.
- *"Can it be gamed by going cheaper-but-dumber?"* → No. Cost is paired with a quality score; a cheaper-but-worse candidate routes to NEEDS_REVIEW, never an automatic pass.
- *"How do you know the gate is right?"* → A 30-scenario labelled eval; it scores 30/30, enforced in CI.
