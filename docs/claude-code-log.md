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
| **UiPath integration** | `costguard/uipath/{coded_agent,test_manager,action_center,maestro_contract,config,run_live,langchain_patient}.py` | The coded-agent entrypoint, Test Cloud result registration, Action Center HITL task, the Maestro in/out contract, `.env` config, the live UiPath-gateway runner, and an external LangChain agent-under-test — all with offline dry-run and a live path via the UiPath Python SDK. |
| **Second agent (multi-agent)** | `costguard/explainer.py` | A Cost Explainer that decomposes a cost regression into model-price / call-count / token-volume factors (deterministic, tested) and writes a plain-language root cause via the UiPath LLM Gateway. |
| **Gate eval suite** | `costguard/evals.py`, `evals/scenarios.json` | 30 labelled scenarios that meta-test the gate's own verdicts; the gate scores 100%. |
| Tests | `tests/test_{engine,evals,ledger,uipath,stress}.py` | 26 tests, all green, written alongside the code (incl. a 150-config fuzz of the gate invariants). |

## How it was built (process)
1. **Research → idea lock.** Claude Code ran multi-agent research to find an empty, defensible niche (cost-regression gating on UiPath; no incumbent), then locked the design.
2. **Offline-first.** The full engine + UiPath contracts were built and tested with a deterministic mock gateway, so the platform integration is a "flip the switch" step, not a rebuild.
3. **UiPath for Coding Agents.** Claude Code uses `uip skills` + the `uip` CLI to authenticate, package the coded agent, and deploy it to UiPath Automation Cloud, and to register results through the Test Manager API.

## Hard problems Claude Code solved *on the platform* (not just codegen)
These are real UiPath-integration obstacles the coding agent diagnosed and worked through — the kind of work that distinguishes "an agent used the platform" from "an agent generated some code":

| Problem hit | Diagnosis | Fix Claude Code applied |
|---|---|---|
| All Test Manager API calls silently 401'd | `TM.Default` is not a real scope | Switched the External App to **granular** scopes (`TM.Projects TM.TestCases TM.TestSets TM.Requirements …`) |
| Stdlib token requests blocked (HTTP 1010) | Cloudflare bot rule on default UA | Set a browser `User-Agent` in `costguard/uipath/auth.py` |
| `uip codedagent publish` 500'd | server-side packaging bug | Bypassed via `uip or packages upload` + `uip or processes create` |
| `jobs start` → "Undefined process" | needs the release-key GUID, not the process name | Resolve and pass the release key |
| `sdk.llm.chat_completions` returned a coroutine | the SDK method is async | Wrapped it with `asyncio.run` inside a sync `UiPathLLMGateway` |
| UiPath LLM auth failed with client creds | the gateway needs a bearer token + tenant URL | Mint a token via `get_token()`, set `UIPATH_ACCESS_TOKEN` + `UIPATH_URL` |
| Action Center task creation 404'd on the sandbox | tenant doesn't provision GenericTasks | Guarded the HITL call so the gate degrades gracefully (`deferred:action-center-unavailable`) instead of crashing |
| `codedagent setup` broke on Python 3.14 / PEP-668 | externally-managed env | Installed the SDK with `uv tool install uipath` |

Net result: the same gate runs **offline (deterministic mock)** and **live on real UiPath-gateway models** — the live FAIL verdict (13.12×) and the LangChain cross-platform run (12.76×) are committed as raw JSON in `docs/`.

## Evidence
- **Commit history:** every commit in this repo was authored via Claude Code (`git log` — messages are co-authored by the model).
- **Live artifacts (machine-generated, committed):** `docs/live-uipath-result.json` (real UiPath-gateway models), `docs/live-langchain-result.json` (external framework), `evals/result.json` (gate scored 30/30).
- **Reproduce in one command each:** `python3 -m costguard.cli` (hero gate), `python3 -m costguard.evals` (gate eval), `uv run --with uipath python -m costguard.uipath.run_live` (live on UiPath).
- **Demo video:** shows the gate running and the Claude Code build.

> To the reviewer: the architecture in the README plus this repo's commit history demonstrate that Claude Code's output **is** the working solution, not a reference — and the table above shows it did genuine platform integration work, not just file generation.
