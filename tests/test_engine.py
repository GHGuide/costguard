"""Engine tests — run with: python -m pytest  (or python tests/test_engine.py)

No third-party deps required; falls back to a tiny runner if pytest is absent.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from costguard.dataset import make_invoices
from costguard.gateway import MockGateway
from costguard.patient import AgentConfig, InvoiceExtractionAgent
from costguard.runner import run_config
from costguard.stats import summarize, cost_per_success
from costguard.verdict import decide


def _setup():
    invoices = make_invoices(n=8, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())
    return invoices, agent


def test_deterministic():
    invoices, agent = _setup()
    cfg = AgentConfig("v1", "claude-haiku-4-5")
    a = summarize("a", run_config(agent, cfg, invoices, repeats=10, seed=1))
    b = summarize("b", run_config(agent, cfg, invoices, repeats=10, seed=1))
    assert a.cost_per_success == b.cost_per_success
    assert a.total_cost == b.total_cost


def test_cost_regression_fails_gate():
    invoices, agent = _setup()
    base = summarize("v1", run_config(agent, AgentConfig("v1", "claude-haiku-4-5", "simple", 0.92),
                                      invoices, repeats=20, seed=1))
    cand = summarize("v2", run_config(agent, AgentConfig("v2", "claude-sonnet-4-6", "verify", 0.94),
                                      invoices, repeats=20, seed=2))
    assert cand.cost_per_success > base.cost_per_success
    assert decide(base, cand).verdict == "FAIL"


def test_equivalent_change_passes():
    invoices, agent = _setup()
    cfg = AgentConfig("v1", "claude-haiku-4-5", "simple", 0.92)
    base = summarize("v1", run_config(agent, cfg, invoices, repeats=20, seed=1))
    cand = summarize("v2", run_config(agent, cfg, invoices, repeats=20, seed=2))
    assert decide(base, cand).verdict in ("PASS", "NEEDS_REVIEW")


def test_cost_per_success_infinite_when_no_success():
    from costguard.runner import RunRecord
    recs = [RunRecord("d", 0.01, 100, False, 0.0)]
    assert cost_per_success(recs) == float("inf")


def test_pricing_prefix_resolves_dated_model():
    from costguard.pricing import resolve, cost_usd
    assert resolve("claude-haiku-4-5-20251001") == resolve("claude-haiku-4-5")
    assert cost_usd("claude-haiku-4-5-20251001", 1_000_000, 0) == 1.00


def test_real_gateway_errors_without_key():
    # Construction must fail cleanly (no network, no key) rather than hang.
    import os
    from costguard.gateway import AnthropicGateway
    saved = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        raised = False
        try:
            AnthropicGateway()
        except (RuntimeError, ImportError):
            raised = True
        assert raised
    finally:
        if saved is not None:
            os.environ["ANTHROPIC_API_KEY"] = saved


def test_real_parse_path_scores_model_json():
    # A fake "real" gateway returning clean JSON should be parsed + scored, not simulated.
    from costguard.gateway import LLMGateway, LLMResult
    from costguard.patient import InvoiceExtractionAgent, AgentConfig
    from costguard.quality import is_success

    inv = {"id": "x", "text": "...", "ground_truth": {
        "invoice_number": "INV-1", "vendor": "Acme", "total": 12.50,
        "currency": "USD", "due_date": "2026-01-01"}}

    class FakeReal(LLMGateway):
        produces_text = True
        def complete(self, model, prompt, max_output_tokens=400):
            txt = ('{"invoice_number":"INV-1","vendor":"Acme","total":"12.50",'
                   '"currency":"USD","due_date":"2026-01-01"}')
            return LLMResult(txt, "claude-haiku-4-5", 100, 40)

    import random as _random
    agent = InvoiceExtractionAgent(FakeReal())
    res = agent.run(inv, AgentConfig("v", "claude-haiku-4-5"), _random.Random(0))
    assert is_success(res["extracted"], inv["ground_truth"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
