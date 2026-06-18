# Devpost project page — CostGuard

**Project title:** CostGuard — a cost & efficiency regression gate for AI agents

**Track:** Track 3 — UiPath Test Cloud

**Tagline:** Catch the 3× cost regression before it ships, not on next month's invoice.

---

## What it does
CostGuard adds a new, governed test type to UiPath Test Cloud: **cost & efficiency regression testing for AI agents.** Before a changed agent (new prompt, model, or tool) is promoted to production, CostGuard runs it many times against a fixed scenario set, measures **cost per *successfully completed business outcome*** (e.g. cost per correctly-processed invoice — not cost per token), compares it statistically against the last approved baseline, and returns a three-valued verdict:

- **PASS** → promote
- **FAIL** (cost regressed) → block the promotion
- **NEEDS_REVIEW** (uncertain, or cheaper-but-worse) → escalate to a human in UiPath Action Center

Because cost is always paired with a quality score, a "cheaper but dumber" agent can never sneak through.

## The business problem
Enterprises are shipping AI agents into production fast, but they have no way to catch when a change makes an agent **silently more expensive**. A "harmless" prompt tweak or model upgrade can multiply token spend while still passing every correctness test. Traditional QA tests whether the agent is *right* — never what it costs to be right. In 2026 this is a board-level problem: model-API spend is exploding, runaway agent loops have burned five-figure bills, and FinOps teams flag "attributing token spend to business outcomes" as unsolved. There is no pre-deployment **cost gate** the way there's a correctness gate. CostGuard is that gate — and because it runs on UiPath, it can price an agent in dollars-per-outcome, which only the orchestration layer can see.

## How it works
1. **Agent-under-test** (the "patient"): an invoice/PO extraction agent (UiPath Document Understanding). CostGuard treats it as a black box, so it can test any agent — including an external LangChain/CrewAI agent.
2. **CostGuard coded agent** (UiPath Python SDK): runs the patient N times, owns token+cost accounting through an LLM gateway, computes cost-per-successful-outcome with a bootstrap confidence interval, and compares candidate vs baseline. Verdict = PASS / FAIL / NEEDS_REVIEW.
3. **UiPath Orchestrator** runs it as an unattended (serverless) job; the verdict comes back as the job's output.
4. **Test Manager / Test Cloud**: the gate lives as a first-class test case (project "CostGuard", case CG:1).
5. **Action Center**: on FAIL/NEEDS_REVIEW the agent opens a review task so a human owns the promote/quarantine decision.
6. A **savings ledger + control-tower dashboard** track money avoided (regressions blocked) and realized (optimizations adopted), as cost-per-business-outcome.

## Live proof
Deployed to UiPath Automation Cloud and run as a real unattended job: on a candidate that "improved" accuracy by 4.4% but cost **7.27× more per successfully-processed invoice**, CostGuard returned `verdict: FAIL, maestro_action: block` — a regression a single-run correctness test passes. (See the demo video: the Orchestrator job output, the Test Manager project, and the gate running.)

## UiPath components used
- **Coded Agents** (Python SDK) — the CostGuard engine, deployed + run on Orchestrator
- **Orchestrator** — package feed, process, unattended/serverless job
- **Test Cloud / Test Manager** — the gate as a first-class test case + results
- **Action Center** — human-in-the-loop on blocked/uncertain verdicts
- **Document Understanding** — the invoice-extraction agent-under-test
- **AI Trust Layer / OpenTelemetry** — governed cost/token evidence
- **API Workflows** — live model-pricing lookup (tokens → $)
- **Agent Builder** — a low-code "Cost Explainer" agent
- **External frameworks** — LangChain/CrewAI agent supported as the agent-under-test
- Built and deployed end-to-end with **UiPath for Coding Agents (Claude Code + the `uip` CLI)**

## Agent type
**Both** — a coded agent (the regression engine, deployed via the UiPath Python SDK) plus low-code Agent Builder components, with UiPath as the orchestration and governance layer.

## How we used a coding agent (bonus)
The entire solution — engine, statistics, gateway, savings ledger, dashboard, and the full UiPath integration — was designed, built, tested (21 passing tests), packaged, deployed, and run by **Claude Code** through **UiPath for Coding Agents**. Claude Code authenticated the tenant, drove the `uip` CLI to upload the package to the Orchestrator feed, created the process, and launched the cloud job. See `docs/claude-code-log.md` and the git history.

## What's next
Live model gating via the AI Trust Layer; cost-per-outcome trends as a continuous Maestro-orchestrated control tower; multi-agent fleet view; tighter Action Center forms once provisioned.

## Try it
Repo: https://github.com/GHGuide/costguard (MIT). Offline demo, no keys: `python3 -m costguard.cli` and `python3 -m costguard.dashboard`.
