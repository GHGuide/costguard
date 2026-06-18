# CostGuard — Demo video script (≤5:00)

Track 3 (UiPath Test Cloud). Rules: must show it RUNNING (not slides), walk the architecture, name the agents + orchestration, show where humans fit, and show Claude Code building it (bonus). Have this recording as the backup for the live finale too.

**Setup before recording:** terminal in the project folder with `export PATH="$HOME/.local/bin:$PATH"`; UiPath portal open in a browser tab (Orchestrator → Jobs, and Test Manager → CostGuard); `uip` already logged in.

---

### 0:00–0:35 — The problem (hook, talk over a terminal)
> "Teams ship changes to AI agents every day — a new prompt, a bigger model. A change can pass every correctness test and still quietly **triple what the agent costs to run**. You find out on next month's invoice. In 2026 that's a board-level problem — model spend is exploding. There's no gate for it. **CostGuard** is that gate."

On screen: title + one line — *"CostGuard: a cost & efficiency regression gate for AI agents, on UiPath."*

### 0:35–1:20 — The gate, running (offline engine = instant, real)
Run:
```bash
python3 -m costguard.cli
```
> "Here's the gate on a UiPath invoice-extraction agent. Baseline v1 vs a candidate v2 that 'improved' the prompt and upgraded the model. CostGuard runs each version many times, and measures the metric that matters: **cost per *successfully* processed invoice** — not cost per token."

Point at the verdict: **FAIL — 7.27× cost for +4.4% accuracy → blocked.**
> "Quality barely moved. Cost-per-invoice went up 7×. CostGuard blocks the promotion. A normal one-shot test would have passed this."

### 1:20–1:55 — Why it's not just a FinOps alert (the dashboard)
Run:
```bash
python3 -m costguard.dashboard
```
> "Because it's a *test*, not an alert. It runs before promotion, pairs cost with quality so 'cheaper but dumber' can't sneak through, and tracks the savings: regressions blocked, optimizations adopted — cost per **business outcome**, the number finance actually cares about."

### 1:55–3:10 — It runs ON UiPath (the core)
Switch to the **UiPath portal**.
- **Test Manager → CostGuard** project + test case `CG:1` — "the gate is a first-class Test Cloud test."
- **Orchestrator → Processes (Shared)** → "CostGuard Gate" — "the coded agent, deployed as a process."
- **Orchestrator → Jobs** → open the Successful job → **Output Arguments** showing `verdict: FAIL, maestro_action: block, cost_ratio: 7.272`.
> "This is a real unattended job on UiPath Automation Cloud — serverless robot — returning the blocking verdict. Orchestrator runs it; on FAIL the agent escalates to a human in Action Center to approve or quarantine. Humans stay accountable for the high-impact call."

### 3:10–4:20 — Built + deployed by Claude Code (the bonus)
Back to terminal. Show a short real sequence:
```bash
uip codedagent run main '{}'        # the agent runs in the UiPath runtime
uip or packages upload .uipath/costguard_gate.0.0.3.nupkg
uip or jobs start <release-key> --folder-path Shared
```
> "Every line of this — the engine, the statistics, the coded agent, the UiPath integration — was built and deployed by **Claude Code driving the UiPath CLI**, through UiPath for Coding Agents. Claude Code authenticated the tenant, packaged the agent, uploaded it to the feed, created the process, and launched the job."

(Optionally show a 5-second clip of Claude Code editing `main.py` / running `uip`.)

### 4:20–5:00 — Impact + close
> "CostGuard turns runaway agent spend into a governed, pre-production gate — catch the 3× regression before it ships, not on the invoice. It's a coded agent plus low-code UiPath components: Orchestrator, Test Cloud, Action Center, Document Understanding, and the AI Trust Layer for cost evidence — with UiPath as the governance layer tying it together. That's how you operate and govern agents at scale."

End card: repo URL (github.com/GHGuide/costguard) + "Built with Claude Code + UiPath."

---
**Honesty notes (don't overclaim on camera):** the live cloud *job + verdict* are real; show them. The Action Center task is wired in code but the sandbox tenant's task endpoint is disabled — say "escalates to Action Center" and show the `maestro_action: block` + the code, don't fake a task. Keep cost dollar figures labelled as illustrative where they come from the mock gateway; the **ratio (7.27×)** and the method are real.
