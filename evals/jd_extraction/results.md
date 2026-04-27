# JD Extraction Eval Results

**Model:** gpt-5.4-mini (resolves to `gpt-5.4-mini-2026-03-17`)
**Date:** 2026-04-27
**Threshold:** 7/8

## Results: 8/8 PASS

| # | Fixture | Result |
|---|---------|--------|
| 1 | Corporate SWE with boilerplate | PASS |
| 2 | Terse startup backend engineer | PASS |
| 3 | Academic postdoc in computational biology | PASS |
| 4 | Ambiguous seniority software engineer | PASS |
| 5 | Fintech engineer with compliance language | PASS |
| 6 | Site Reliability Engineer | PASS |
| 7 | ML Engineer hard-vs-nice classification | PASS |
| 8 | Product Manager non-engineering role | PASS |

## Grading criteria

Each fixture is graded on:
1. **No missed hard requirements** — key required skills appear in `hard_requirements`
2. **No boilerplate in requirements** — DEI/legal/benefits text absent from `hard_requirements`
3. **Correct hard-vs-nice classification** — nice-to-have items are not misclassified as hard requirements
4. **Seniority** — inferred level matches acceptable options
5. **Culture signals** — minimum expected count present (where applicable)

## Re-running evals

```bash
source .env
uv run python -m evals.jd_extraction.run_evals
# Expected: 8/8 passed, Verdict: PASS ✓
```
