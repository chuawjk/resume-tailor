#!/usr/bin/env python
"""Gap Analysis agent eval runner.

Runs each fixture through analyse_gaps and grades the result against
the criteria defined in fixtures.py.

Grading criteria (per backlog):
  1. expected_in_strong  — substrings that must appear in strong_matches
  2. expected_in_gaps    — substrings that must appear in gaps[i]["requirement"]
  3. total_requirements  — total classified must equal hard + nice-to-have count

Ship threshold: 4 of 5 fixtures pass all checks.

Usage:
    OPENAI_API_KEY=sk-... uv run python evals/agents/gap_analysis/run_evals.py

Optional env vars:
    RESUME_TAILOR_MODEL   — override model (default: gpt-5.4-mini)
    EVAL_VERBOSE          — set to 1 to print full extraction results
"""

import os
import sys
import textwrap

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, _ROOT)

from evals.agents.gap_analysis.fixtures import FIXTURES  # noqa: E402
from resume_tailor.agents.gap_analysis.agent import analyse_gaps  # noqa: E402

SHIP_THRESHOLD = 4
VERBOSE = os.environ.get("EVAL_VERBOSE") == "1"


# ---------------------------------------------------------------------------
# Grading helpers
# ---------------------------------------------------------------------------


def grade(result: dict, checks: dict) -> list[str]:
    """Return a list of failure messages. Empty list means all checks passed."""
    failures = []

    strong = result.get("strong_matches", [])
    gaps = [g["requirement"] for g in result.get("gaps", [])]
    weak = result.get("weak_matches", [])
    all_buckets = strong + [w["requirement"] for w in weak] + gaps

    for phrase in checks.get("expected_in_strong", []):
        if not any(phrase.lower() in s.lower() for s in strong):
            failures.append(f"MISS strong: '{phrase}' not found in strong_matches")

    for phrase in checks.get("expected_in_gaps", []):
        if not any(phrase.lower() in g.lower() for g in gaps):
            failures.append(f"MISS gap: '{phrase}' not found in gaps")

    total_expected = checks.get("total_requirements", 0)
    total_classified = len(all_buckets)
    if total_classified != total_expected:
        failures.append(f"DROPPED: classified {total_classified} of {total_expected} requirements")

    return failures


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_evals() -> bool:
    """Run all gap analysis fixtures. Returns True if the suite passes the ship threshold."""
    results = []
    print(f"Running {len(FIXTURES)} eval fixtures...\n")

    for i, fixture in enumerate(FIXTURES, 1):
        name = fixture["name"]
        print(f"[{i}/{len(FIXTURES)}] {name} ... ", end="", flush=True)

        try:
            result = analyse_gaps(
                fixture["jd_profile"],
                fixture["cv_profile"],
                temperature=0.0,
            )
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

    return passed >= SHIP_THRESHOLD


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    sys.exit(0 if run_evals() else 1)
