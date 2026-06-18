# CostGuard — presentation deck (slide-by-slide)

Fill the official AgentHack template with these. ~10 slides. Keep one idea per slide; lead with the problem and the headline number.

**Slide 1 — Title**
CostGuard — a cost & efficiency regression gate for AI agents.
Track 3: UiPath Test Cloud. Built with Claude Code + UiPath. Repo + demo links.

**Slide 2 — The problem**
A change to an AI agent (prompt/model/tool) can pass every correctness test and still **triple what it costs to run**. You find out on the invoice. 2026: model spend exploding, runaway agents burning five-figure bills, no pre-deploy cost gate. QA tests if the agent is *right* — never what it costs to be right.

**Slide 3 — The insight**
Cost alone is gameable (cheaper-but-dumber). The right metric is **cost per *successfully completed business outcome*** (cost per correctly-processed invoice). Only the orchestration layer — UiPath — knows the business-outcome boundary. That's the un-clonable angle.

**Slide 4 — The solution**
CostGuard: a new test type in Test Cloud. Run the agent N times → cost-per-outcome + confidence interval → compare to baseline → **PASS (promote) / FAIL (block) / NEEDS_REVIEW (human)**. Cost paired with quality. A gate, not an alert.

**Slide 5 — Live proof (the headline)**
Candidate "improved" accuracy +4.4% but cost **7.27× more per invoice** → **FAIL / block.** A single-run correctness test passes it; CostGuard catches it. Screenshot: the Orchestrator job output (`verdict: FAIL, maestro_action: block, cost_ratio: 7.272`).

**Slide 6 — Architecture (diagram)**
Agent-under-test (Document Understanding / external LangChain) → CostGuard coded agent (Python SDK, owns cost accounting) → verdict → Orchestrator job → Test Cloud result → FAIL routes to Action Center (human) → promote/quarantine. AI Trust Layer = cost evidence. UiPath = governance layer.

**Slide 7 — Platform usage (depth)**
Coded Agent + Orchestrator (feed/process/serverless job) + Test Cloud/Test Manager + Action Center + Document Understanding + AI Trust Layer/OTel + API Workflows + Agent Builder + external framework support. Deliberate, load-bearing — remove UiPath and it collapses.

**Slide 8 — Built by a coding agent (bonus)**
100% built, tested, packaged, deployed, and run by **Claude Code via UiPath for Coding Agents** (`uip` CLI). 21 passing tests. Show a screenshot of Claude Code driving `uip` + the successful job.

**Slide 9 — Impact & adoption**
Turns runaway agent spend into a governed pre-production gate. Savings ledger: $ avoided (regressions blocked) + realized (optimizations adopted), cost-per-business-outcome. Scales to any agent, any framework. Buyers: platform/FinOps/QA leads. Ties to agent governance + cost-control mandates.

**Slide 10 — What's next + close**
Live-model gating via AI Trust Layer; continuous cost-per-outcome control tower (Maestro); fleet view. "Catch the 3× regression before it ships, not on the invoice." Repo + demo links.

---
Design tips: dark theme to match UiPath; one big number per slide (7.27×, the $/yr); the architecture diagram (slide 6) is the centerpiece — reuse the README ASCII or redraw it cleanly. Be honest: live cloud job + verdict are real; label any illustrative dollar figures.
