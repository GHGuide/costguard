# CostGuard — an agentic cost & efficiency regression gate for AI agents

**UiPath AgentHack 2026 · Track 3 (UiPath Test Cloud)**

License: MIT · Agent type: **both** (a coded agent + a low-code UiPath agent) · Built with **Claude Code** via UiPath for Coding Agents.

---

## Project description

Enterprises now ship AI agents into production fast, but they have no way to catch when a change makes an agent **silently more expensive**. A "harmless" prompt tweak or model upgrade can multiply token spend while still passing a correctness test. Traditional QA tests *whether the agent is right* — never *what it costs to be right*.

**CostGuard adds a new, governed test type to UiPath Test Cloud: cost & efficiency regression testing.** Before a changed agent is promoted to production, CostGuard runs it many times against a fixed scenario set, measures **cost per successfully-completed business outcome** (e.g. cost per correctly-processed invoice — *not* cost per token), compares it statistically against the last approved baseline, and:

- **PASS** → promote,
- **FAIL** (cost regressed) → block,
- **NEEDS_REVIEW** (uncertain, or cheaper-but-worse) → route to a human in UiPath Action Center.

Because cost is paired with a quality score, a "cheaper but dumber" agent can never sneak through.

> **Why cost-per-*outcome*:** only UiPath knows the business-process boundary an agent serves, so CostGuard can price an agent in dollars-per-invoice instead of dollars-per-token — the attribution problem FinOps practitioners flagged as unsolved in 2026.

### The hero result (runs offline, today)
```
COST / SUCCESS        $0.0009   →   $0.0069     (7.28x)
quality delta                        +4.4% accuracy
VERDICT: FAIL ⛔  — "+4.4% accuracy is not worth 7.28x cost"  → promotion blocked
```
A candidate that *looks* better (higher accuracy, passes correctness tests) is **7× more expensive per correctly-processed invoice**. CostGuard catches it before it ships.

## Architecture

![CostGuard architecture — the gate runs on UiPath; FAIL blocks promotion, NEEDS_REVIEW escalates to a human in Action Center](docs/architecture.svg)

## How it works

```
 change to agent (prompt/model/tool)
        │
        ▼
 ┌──────────────────────── UiPath Maestro (orchestration + governance) ───────────────────────┐
 │   Patient = invoice/PO extraction agent  ──run N times over a Test Cloud scenario set──┐    │
 │   (UiPath Document Understanding + Agent Builder, or an external LangChain/CrewAI agent)│    │
 │                                                                                        ▼    │
 │   CostGuard coded agent (Python SDK)                                                         │
 │     • LLM gateway wraps every call → owns token + $ accounting  (+ AI Trust Layer/OTel)      │
 │     • cost-per-successful-outcome + bootstrap confidence interval                            │
 │     • statistical compare vs last green baseline → PASS / FAIL / NEEDS_REVIEW                │
 │     • registers result in Test Cloud (Test Manager API)                                      │
 │                                                                                        │    │
 │   FAIL → block promotion        NEEDS_REVIEW → UiPath Action Center (human decides) ◄──┘    │
 └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## UiPath components used
- **UiPath Test Cloud / Test Manager API** — cost regression registered as a first-class test result; the gate.
- **UiPath Maestro** — orchestrates the regression run and the promote/block/escalate flow.
- **Coded Agent (Python SDK)** — the CostGuard engine in this repo.
- **Agent Builder (low-code)** — the patient invoice-extraction agent + a "Cost Explainer" agent.
- **Document Understanding** — invoice/PO field extraction (the patient).
- **API Workflows** — live model-pricing lookup (tokens → $).
- **AI Trust Layer / OpenTelemetry agent traces** — governed cost/token evidence.
- **Action Center** — human-in-the-loop on FAIL / NEEDS_REVIEW.
- **External framework** — the patient can be a LangChain / CrewAI agent (validating a third-party agent inside a UiPath-orchestrated process).

> Status: the **engine, statistics, gateway, and gate logic are complete and run offline today** (see below). The UiPath platform wiring is in progress on UiPath Automation Cloud (UiPath Labs).

## Setup / run the demo (no API key, no platform access needed)
Requires Python 3.10+ and nothing else.
```bash
python3 -m costguard.cli           # human-readable gate report (the hero demo)
python3 -m costguard.cli --json    # machine-readable report (what Test Cloud registers)
python3 -m costguard.dashboard     # the control tower: savings ledger + fleet + cost-per-outcome trend
python3 tests/test_engine.py       # engine tests
python3 tests/test_ledger.py       # ledger / savings-math tests
```
### Run against real LLMs
Set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) in `.env`, then:
```bash
python3 -m costguard.live --provider anthropic \
    --baseline claude-haiku-4-5 --candidate claude-sonnet-4-6 \
    --candidate-strategy verify --n 6 --repeats 3
```
Same engine and verdict logic — only the gateway changes, so real token usage and real extraction quality flow through unchanged. Provider adapters (`AnthropicGateway`, `OpenAIGateway`) return true token counts and retry transient errors.

To test your own two agent versions, edit `BASELINE` / `CANDIDATE` in `costguard/cli.py`, or import `run_config`, `summarize`, `decide` and feed your own agent (any object exposing the patient contract).

## Agent type
**Both.** A **coded agent** (the Python regression engine, deployed via the UiPath Python SDK) plus **low-code Agent Builder agents** (the invoice-extraction patient and the Cost Explainer). External LangChain/CrewAI agents are supported as the agent-under-test.

## How Claude Code built this
This solution was built **with Claude Code** (Anthropic) through **UiPath for Coding Agents**.
- **What it did:** scaffolded the entire coded engine (gateway, pricing, statistics, verdict, runner, report, CLI), designed the cost-per-outcome metric and the three-valued gate, wrote the tests, and (in progress) drives the `uip` CLI to pack/deploy the coded agent and wire the Test Cloud / Maestro / Action Center integration.
- **Evidence:** see [`docs/claude-code-log.md`](docs/claude-code-log.md) for prompt/session excerpts and screenshots. *(maintained during the build)*

## Repository layout
```
costguard/        engine: gateway, pricing, dataset, patient, quality, runner, stats, verdict, report, cli
tests/            engine tests
BRIEF.md          problem, idea, why-it-wins, judging map, milestones
RULES.md          hackathon rules (reference)
PROGRESS.md       running build log
```
