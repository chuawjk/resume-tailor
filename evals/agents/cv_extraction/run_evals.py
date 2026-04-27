#!/usr/bin/env python
"""CV Extraction agent eval runner.

Runs each fixture CV through extract_cv and grades the result against
the criteria defined in fixtures.py.

Grading criteria (per backlog):
  1. Name extraction — required_name must appear in personal.name
  2. Experience roles — each phrase in required_in_experience_roles must appear
     in at least one experience entry's role field
  3. Technical skills — each phrase in required_technical_skills must appear
     in skills.technical
  4. Experience count — number of experience entries must meet min_experience_count

Ship threshold: 3 of 4 fixtures pass all checks.

Usage:
    OPENAI_API_KEY=sk-... uv run python evals/agents/cv_extraction/run_evals.py

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

from evals.agents.cv_extraction.fixtures import FIXTURES  # noqa: E402
from resume_tailor.agents.cv_extraction.agent import extract_cv  # noqa: E402

SHIP_THRESHOLD = 3
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

    # Check personal name
    required_name = checks.get("required_name", "")
    if required_name:
        actual_name = result.get("personal", {}).get("name", "")
        if required_name.lower() not in actual_name.lower():
            failures.append(
                f"NAME: '{required_name}' not found in personal.name (got '{actual_name}')"
            )

    # Check experience roles
    experience = result.get("experience", [])
    experience_roles = [e.get("role", "") for e in experience]
    for phrase in checks.get("required_in_experience_roles", []):
        if not _contains_any(experience_roles, phrase):
            failures.append(f"MISS experience role: '{phrase}' not found in any experience.role")

    # Check technical skills
    technical = result.get("skills", {}).get("technical", [])
    for phrase in checks.get("required_technical_skills", []):
        if not _contains_any(technical, phrase):
            failures.append(f"MISS technical skill: '{phrase}' not found in skills.technical")

    # Check minimum experience count
    min_count = checks.get("min_experience_count", 0)
    if len(experience) < min_count:
        failures.append(f"EXPERIENCE COUNT: got {len(experience)}, expected at least {min_count}")

    return failures


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_evals() -> bool:
    """Run all CV extraction fixtures. Returns True if the suite passes the ship threshold."""
    results = []
    print(f"Running {len(FIXTURES)} eval fixtures...\n")

    for i, fixture in enumerate(FIXTURES, 1):
        name = fixture["name"]
        print(f"[{i}/{len(FIXTURES)}] {name} ... ", end="", flush=True)

        try:
            result = extract_cv(fixture["cv"], temperature=0.0)
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
