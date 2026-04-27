#!/usr/bin/env python
"""Top-level eval runner. Discovers and runs all agent eval suites under evals/agents/.

Usage:
    OPENAI_API_KEY=sk-... uv run python -m evals.run_evals

Optional env vars:
    RESUME_TAILOR_MODEL   — override model (default: gpt-5.4-mini)
    EVAL_VERBOSE          — set to 1 to print full extraction results
"""

import importlib
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, _ROOT)


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")
    suites = sorted(
        name
        for name in os.listdir(agents_dir)
        if os.path.isfile(os.path.join(agents_dir, name, "run_evals.py"))
    )

    if not suites:
        print("No eval suites found under evals/agents/.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(suites)} eval suite(s): {', '.join(suites)}\n")

    results: dict[str, bool] = {}
    for suite in suites:
        print(f"{'=' * 60}")
        print(f"Suite: {suite}")
        print(f"{'=' * 60}")
        module = importlib.import_module(f"evals.agents.{suite}.run_evals")
        results[suite] = module.run_evals()
        print()

    all_passed = all(results.values())
    print(f"{'=' * 60}")
    print(f"Overall ({len(suites)} suite(s)): {'PASS ✓' if all_passed else 'FAIL ✗'}")
    for suite, passed in results.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {suite}")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
