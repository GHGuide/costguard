"""Run the gate against REAL LLMs.

    python -m costguard.live --provider anthropic \
        --baseline claude-haiku-4-5 --candidate claude-sonnet-4-6 \
        --candidate-strategy verify --n 6 --repeats 3

Needs ANTHROPIC_API_KEY (or OPENAI_API_KEY) in your environment or .env.
Same engine, same verdict logic as the offline demo — only the gateway changes,
so real token usage and real extraction quality flow through unchanged.
"""

from __future__ import annotations

import argparse
import json
import sys

from .cli import _print_human
from .dataset import make_invoices
from .env import load_dotenv
from .gateway import AnthropicGateway, MockGateway, OpenAIGateway
from .patient import AgentConfig, InvoiceExtractionAgent
from .report import build_report
from .runner import run_config
from .stats import summarize
from .verdict import decide


def _make_gateway(provider: str):
    if provider == "anthropic":
        return AnthropicGateway()
    if provider == "openai":
        return OpenAIGateway()
    if provider == "mock":
        return MockGateway()
    raise SystemExit(f"unknown provider {provider!r} (anthropic | openai | mock)")


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    ap = argparse.ArgumentParser(prog="costguard.live")
    ap.add_argument("--provider", default="anthropic", choices=["anthropic", "openai", "mock"])
    ap.add_argument("--baseline", default="claude-haiku-4-5")
    ap.add_argument("--candidate", default="claude-sonnet-4-6")
    ap.add_argument("--baseline-strategy", default="simple", choices=["simple", "verify"])
    ap.add_argument("--candidate-strategy", default="verify", choices=["simple", "verify"])
    ap.add_argument("--n", type=int, default=6, help="invoices in the scenario set")
    ap.add_argument("--repeats", type=int, default=3, help="runs per invoice per version")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        gateway = _make_gateway(args.provider)
    except (RuntimeError, ImportError) as e:
        print(f"Cannot start {args.provider} gateway: {e}", file=sys.stderr)
        print("Set the API key in .env, or run the offline demo: python -m costguard.cli",
              file=sys.stderr)
        return 2

    invoices = make_invoices(n=args.n, seed=7)
    agent = InvoiceExtractionAgent(gateway)
    base_cfg = AgentConfig(f"base · {args.baseline}", args.baseline, args.baseline_strategy)
    cand_cfg = AgentConfig(f"cand · {args.candidate}", args.candidate, args.candidate_strategy)

    print(f"Running {args.provider}: {args.n} invoices x {args.repeats} repeats x 2 versions "
          f"= {args.n * args.repeats * 2} live calls ...", file=sys.stderr)

    base = summarize(base_cfg.name, run_config(agent, base_cfg, invoices, repeats=args.repeats, seed=1))
    cand = summarize(cand_cfg.name, run_config(agent, cand_cfg, invoices, repeats=args.repeats, seed=2))
    report = build_report(base, cand, decide(base, cand))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
