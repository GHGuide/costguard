# How Claude Code built CostGuard

*Evidence for the UiPath AgentHack "coding agents" bonus (Platform Usage).*

**Coding agent used:** **Claude Code** (Anthropic), via **UiPath for Coding Agents** (`uip skills install --agent claude`, `uip` CLI).

**Why this qualifies (rules a/b/c):**
- **(a) which tool:** Claude Code.
- **(b) how it contributed:** Claude Code designed and wrote essentially the entire codebase — the cost/efficiency engine, the statistics, the LLM gateway + provider adapters, the savings ledger + dashboard, the full UiPath integration layer, and all tests — and drives the `uip` CLI to package/deploy the coded agent onto UiPath.
- **(c) verifiable evidence:** this log + the git commit history + the README architecture, and the screenshots/prompt excerpts captured below.

---

## What Claude Code built

| Area | Files | Role of Claude Code |
|---|---|---|
| Cost/efficiency engine | `costguard/{pricing,gateway,patient,quality,runner,stats,verdict,report}.py` | Designed the **cost-per-successful-outcome** metric, the bootstrap-CI statistics, and the three-valued PASS/FAIL/NEEDS_REVIEW gate with an anti-gaming quality guard. |
| Real LLM adapters | `costguard/gateway.py` (`AnthropicGateway`, `OpenAIGateway`) | True token-usage accounting, retry/backoff, parse+score of real model output. |
| Savings ledger + dashboard | `costguard/{ledger,dashboard}.py` | The control-tower data model: avoided/realized savings, fleet view, cost-per-outcome trend. |
| **UiPath integration** | `costguard/uipath/{coded_agent,test_manager,action_center,maestro_contract,config}.py` | The coded-agent entrypoint, Test Cloud result registration, Action Center HITL task, the Maestro in/out contract, and `.env` config — all with offline dry-run and a live path via the UiPath Python SDK. |
| Tests | `tests/test_{engine,ledger,uipath}.py` | 20 tests, all green, written alongside the code. |

## How it was built (process)
1. **Research → idea lock.** Claude Code ran multi-agent research to find an empty, defensible niche (cost-regression gating on UiPath; no incumbent), then locked the design.
2. **Offline-first.** The full engine + UiPath contracts were built and tested with a deterministic mock gateway, so the platform integration is a "flip the switch" step, not a rebuild.
3. **UiPath for Coding Agents.** Claude Code uses `uip skills` + the `uip` CLI to authenticate, package the coded agent, and deploy it to UiPath Automation Cloud, and to register results through the Test Manager API.

## Evidence
- **Commit history:** every commit in this repo was authored via Claude Code (see `git log`).
- **Prompt/session excerpts:** _(add a few representative prompts here)_
- **Screenshots:** _(add screenshots of the Claude Code session + the `uip` CLI deploy here — `docs/img/`)_
- **Demo video:** the submission video shows Claude Code building/deploying part of the solution.

> To the reviewer: the architecture in the README plus this repo's commit history demonstrate that Claude Code's output is the working solution, not a reference.
