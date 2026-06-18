"""CostGuard coded agent — the cost & efficiency regression gate, deployed to UiPath.

UiPath invokes main(GateInput) -> GateVerdict. It runs the agent-under-test N
times via the CostGuard engine, computes cost-per-successful-outcome with a
confidence interval, compares candidate vs baseline, and returns a three-valued
verdict + the Maestro action (promote / block / escalate).

Runtime-safe: pure computation, no file writes. Uses the deterministic engine so
the gate is reproducible; swap MockGateway for a real provider to gate live models.
"""

from dataclasses import dataclass

from costguard.dataset import make_invoices
from costguard.gateway import MockGateway
from costguard.patient import AgentConfig, InvoiceExtractionAgent
from costguard.report import build_report
from costguard.runner import run_config
from costguard.stats import summarize
from costguard.uipath.maestro_contract import decide_action
from costguard.verdict import decide


@dataclass
class GateInput:
    baseline_model: str = "claude-haiku-4-5"
    baseline_strategy: str = "simple"
    candidate_model: str = "claude-sonnet-4-6"
    candidate_strategy: str = "verify"
    outcome_unit: str = "invoice"
    n_invoices: int = 12
    repeats: int = 20
    monthly_outcomes: int = 50000


@dataclass
class GateVerdict:
    verdict: str               # PASS | FAIL | NEEDS_REVIEW
    maestro_action: str        # promote | block | escalate
    cost_ratio: float          # candidate cost-per-outcome / baseline
    accuracy_delta: float
    extra_cost_per_1000_outcomes_usd: float
    baseline_cost_per_outcome_usd: float
    candidate_cost_per_outcome_usd: float
    summary: str


def main(input: GateInput) -> GateVerdict:
    invoices = make_invoices(n=input.n_invoices, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())
    base_cfg = AgentConfig("baseline", input.baseline_model, input.baseline_strategy, 0.92)
    cand_cfg = AgentConfig("candidate", input.candidate_model, input.candidate_strategy, 0.94)

    base = summarize("baseline", run_config(agent, base_cfg, invoices, repeats=input.repeats, seed=1))
    cand = summarize("candidate", run_config(agent, cand_cfg, invoices, repeats=input.repeats, seed=2))
    verdict = decide(base, cand)
    report = build_report(base, cand, verdict, cost_per_outcome_unit=input.outcome_unit)

    return GateVerdict(
        verdict=report["verdict"],
        maestro_action=decide_action(report["verdict"]),
        cost_ratio=report["cost_ratio"],
        accuracy_delta=report["accuracy_delta"],
        extra_cost_per_1000_outcomes_usd=report["extra_cost_per_1000_outcomes_usd"],
        baseline_cost_per_outcome_usd=report["baseline"]["cost_per_success_usd"],
        candidate_cost_per_outcome_usd=report["candidate"]["cost_per_success_usd"],
        summary=" | ".join(report["reasons"]),
    )
