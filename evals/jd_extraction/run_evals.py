#!/usr/bin/env python
"""JD Extraction agent eval runner.

Runs each fixture JD through extract_jd and grades the result against
the criteria defined in fixtures.py.

Grading criteria (per backlog):
  1. No fabricated requirements — required_in_hard items must appear
  2. No missed hard requirements — forbidden_in_hard must not appear
  3. Correct hard-vs-nice classification — required_in_nice must appear,
     forbidden_in_nice items must not bleed into nice_to_haves (they belong in hard)

Ship threshold: 7 of 8 fixtures pass all checks.

Usage:
    OPENAI_API_KEY=sk-... uv run python evals/jd_extraction/run_evals.py

Optional env vars:
    RESUME_TAILOR_MODEL   — override model (default: gpt-5.4-mini)
    EVAL_VERBOSE          — set to 1 to print full extraction results
"""

import os
import sys
import textwrap

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, _ROOT)

from evals.jd_extraction.fixtures import FIXTURES  # noqa: E402
from resume_tailor.agents.jd_extraction.agent import extract_jd  # noqa: E402

SHIP_THRESHOLD = 7
VERBOSE = os.environ.get("EVAL_VERBOSE") == "1"


# ---------------------------------------------------------------------------
# Grading helpers
# ---------------------------------------------------------------------------


def _contains_any(items: list[str], substring: str) -> bool:
    """Return True if any item in items contains substring (case-insensitive)."""
    sub = substring.lower()
    return any(sub in item.lower() for item in items)


def grade(result: dict, checks: dict) -> list[str]:
    """Return a list of failure messages. Empty list means all checks passed."""
    failures = []
    hard = result.get("hard_requirements", [])
    nice = result.get("nice_to_haves", [])

    for phrase in checks.get("required_in_hard", []):
        if not _contains_any(hard, phrase):
            failures.append(f"MISS hard_req: '{phrase}' not found in hard_requirements")

    for phrase in checks.get("forbidden_in_hard", []):
        if _contains_any(hard, phrase):
            failures.append(f"FABRICATED/BOILERPLATE in hard_req: '{phrase}' found")

    for phrase in checks.get("required_in_nice", []):
        if not _contains_any(nice, phrase):
            failures.append(f"MISS nice_to_have: '{phrase}' not found in nice_to_haves")

    for phrase in checks.get("forbidden_in_nice", []):
        if _contains_any(nice, phrase):
            failures.append(
                f"MISCLASSIFIED: '{phrase}' found in nice_to_haves but should be hard_requirement"
            )

    seniority_options = checks.get("seniority_options", [])
    if seniority_options:
        actual = result.get("seniority", "").lower()
        if not any(opt.lower() in actual for opt in seniority_options):
            failures.append(
                f"SENIORITY: got '{result.get('seniority')}', expected one of {seniority_options}"
            )

    min_signals = checks.get("culture_signals_min", 0)
    if len(result.get("culture_signals", [])) < min_signals:
        failures.append(
            f"CULTURE SIGNALS: got {len(result.get('culture_signals', []))}, "
            f"expected at least {min_signals}"
        )

    return failures


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_evals() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    results = []
    print(f"Running {len(FIXTURES)} eval fixtures...\n")

    for i, fixture in enumerate(FIXTURES, 1):
        name = fixture["name"]
        print(f"[{i}/{len(FIXTURES)}] {name} ... ", end="", flush=True)

        try:
            result = extract_jd(fixture["jd"])
            failures = grade(result, fixture["checks"])

            if failures:
                print("FAIL")
                for f in failures:
                    print(f"       {f}")
                results.append((name, False, failures, result))
            else:
                print("PASS")
                results.append((name, True, [], result))

        except Exception as exc:
            print(f"ERROR: {exc}")
            results.append((name, False, [f"Exception: {exc}"], None))

        if VERBOSE and results[-1][3]:
            import json

            print(textwrap.indent(json.dumps(results[-1][3], indent=2), "       "))

    # Summary
    passed = sum(1 for _, ok, _, _ in results if ok)
    total = len(results)

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} passed")
    print(f"Threshold: {SHIP_THRESHOLD}/{total}")
    print(f"Verdict: {'PASS ✓' if passed >= SHIP_THRESHOLD else 'FAIL ✗'}")
    print("=" * 60)

    for name, ok, failures, _ in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {name}")
        for f in failures:
            print(f"         {f}")

    sys.exit(0 if passed >= SHIP_THRESHOLD else 1)


if __name__ == "__main__":
    run_evals()
