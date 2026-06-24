"""Cost Explainer — a second agent that root-causes a cost regression.

The gate agent decides PASS/FAIL. When it FAILs, this agent explains WHY the cost
moved, decomposing the cost-per-outcome ratio into the factors a human can act on:
  • model price   — a pricier model (output $/token ratio)
  • call count    — a 'verify' pass that doubles the calls per task
  • token volume  — more tokens per call (verbosity)

Attribution is deterministic and testable. The plain-language summary is generated
by an LLM through a gateway (real models via the UiPath LLM Gateway), so the two
agents — gate + explainer — both run governed by UiPath.
"""

from __future__ import annotations

from .patient import AgentConfig
from .pricing import resolve


def _calls(strategy: str) -> int:
    return 2 if strategy == "verify" else 1


def attribute(base_cfg: AgentConfig, cand_cfg: AgentConfig, report: dict) -> dict:
    """Decompose the candidate/baseline cost ratio into named factors (multipliers)."""
    bp, cp = resolve(base_cfg.model), resolve(cand_cfg.model)
    model_factor = cp["output"] / bp["output"] if bp["output"] else 1.0
    call_factor = _calls(cand_cfg.strategy) / _calls(base_cfg.strategy)
    b, c = report["baseline"], report["candidate"]
    overall = report["cost_ratio"]
    # whatever the model+call factors don't explain, attribute to token volume
    explained = model_factor * call_factor
    token_factor = (overall / explained) if explained else 1.0

    factors = [
        {"name": "model price", "multiplier": round(model_factor, 2),
         "detail": f"{cand_cfg.model} output costs {model_factor:.1f}x {base_cfg.model}"},
        {"name": "verify pass", "multiplier": round(call_factor, 2),
         "detail": f"{_calls(cand_cfg.strategy)} model call(s)/invoice vs {_calls(base_cfg.strategy)}"},
        {"name": "token volume", "multiplier": round(token_factor, 2),
         "detail": "tokens per call (verbosity / longer outputs)"},
    ]
    primary = max(factors, key=lambda f: f["multiplier"])
    return {
        "cost_ratio": round(overall, 2),
        "accuracy_delta": report["accuracy_delta"],
        "factors": factors,
        "primary_driver": primary["name"],
        "worth_it": report["accuracy_delta"] > 0.05,  # >5% accuracy gain might justify cost
    }


def explain(attribution: dict, gateway=None, model: str = "gpt-4.1-mini-2025-04-14") -> str:
    """One- or two-sentence plain-language explanation. Uses the gateway (real LLM,
    e.g. UiPath) when given; otherwise a deterministic template."""
    f = attribution["factors"]
    drivers = ", ".join(f"{x['name']} {x['multiplier']}x" for x in f if x["multiplier"] > 1.1)
    acc = attribution["accuracy_delta"] * 100
    if gateway is not None:
        prompt = (
            "You are a FinOps reviewer. In 2 short sentences, plainly explain why an AI agent's "
            f"cost-per-processed-invoice rose {attribution['cost_ratio']}x, given these factors: "
            f"{f}. Accuracy changed {acc:+.1f}%. Say whether the trade looks worth it. No fluff.")
        try:
            return gateway.complete(model, prompt, max_output_tokens=120).text.strip()
        except Exception:  # noqa: BLE001 - explanation must never break the gate
            pass
    return (f"Cost rose {attribution['cost_ratio']}x, driven by {drivers or 'token volume'}; "
            f"accuracy changed {acc:+.1f}% — not worth it." if not attribution["worth_it"]
            else f"Cost rose {attribution['cost_ratio']}x ({drivers}) for {acc:+.1f}% accuracy.")
