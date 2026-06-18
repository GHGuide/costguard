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
    hitl_task_id: str = ""     # Action Center task opened when a human must decide
    hitl_status: str = ""      # created | skipped(pass) | error:<reason>


def _escalate_to_human(report: dict) -> tuple[str, str]:
    """On FAIL / NEEDS_REVIEW, open an Action Center task so a human owns the
    promote/quarantine decision (humans accountable for high-impact calls).
    Guarded: the agent still returns its verdict even if task creation can't run
    (e.g. local dev outside the platform)."""
    if report["verdict"] == "PASS":
        return "", "skipped(pass)"
    try:
        try:
            from uipath.platform import UiPath  # SDK 2.11+
        except ImportError:
            from uipath import UiPath            # fallback for older SDKs
        sdk = UiPath()
        b, c = report["baseline"], report["candidate"]
        schema = {
            "title": "CostGuard cost-regression review",
            "type": "object",
            "properties": {
                "verdict": {"type": "string", "title": "Verdict"},
                "cost_ratio": {"type": "number", "title": "Cost vs baseline (x)"},
                "accuracy_delta": {"type": "number", "title": "Accuracy delta"},
                "extra_cost_per_1000_outcomes_usd": {"type": "number", "title": "Extra $/1000 outcomes"},
                "decision": {"type": "string", "title": "Decision",
                             "enum": ["Approve & promote", "Reject & quarantine"]},
            },
        }
        data = {
            "verdict": report["verdict"],
            "cost_ratio": report["cost_ratio"],
            "accuracy_delta": report["accuracy_delta"],
            "extra_cost_per_1000_outcomes_usd": report["extra_cost_per_1000_outcomes_usd"],
        }
        task = sdk.tasks.create_quickform(
            title=f"CostGuard {report['verdict']}: {report['cost_ratio']:.2f}x cost on candidate",
            task_schema_key="costguard-cost-regression-v1",
            schema=schema,
            data=data,
            folder_path="Shared",
            source_name="CostGuard",
        )
        return str(getattr(task, "id", "") or getattr(task, "key", "")), "created"
    except Exception as e:  # noqa: BLE001 - never fail the gate on HITL issues
        # HITL is wired; if the tenant's Action Center task API is unavailable
        # (e.g. 404 in a sandbox), the gate still returns its blocking verdict.
        reason = "404" if "404" in str(getattr(e, "args", "")) else type(e).__name__
        return "", f"deferred:action-center-unavailable:{reason}"


def main(input: GateInput) -> GateVerdict:
    invoices = make_invoices(n=input.n_invoices, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())
    base_cfg = AgentConfig("baseline", input.baseline_model, input.baseline_strategy, 0.92)
    cand_cfg = AgentConfig("candidate", input.candidate_model, input.candidate_strategy, 0.94)

    base = summarize("baseline", run_config(agent, base_cfg, invoices, repeats=input.repeats, seed=1))
    cand = summarize("candidate", run_config(agent, cand_cfg, invoices, repeats=input.repeats, seed=2))
    verdict = decide(base, cand)
    report = build_report(base, cand, verdict, cost_per_outcome_unit=input.outcome_unit)
    hitl_id, hitl_status = _escalate_to_human(report)

    return GateVerdict(
        verdict=report["verdict"],
        maestro_action=decide_action(report["verdict"]),
        cost_ratio=report["cost_ratio"],
        accuracy_delta=report["accuracy_delta"],
        extra_cost_per_1000_outcomes_usd=report["extra_cost_per_1000_outcomes_usd"],
        baseline_cost_per_outcome_usd=report["baseline"]["cost_per_success_usd"],
        candidate_cost_per_outcome_usd=report["candidate"]["cost_per_success_usd"],
        summary=" | ".join(report["reasons"]),
        hitl_task_id=hitl_id,
        hitl_status=hitl_status,
    )
