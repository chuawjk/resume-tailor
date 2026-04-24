# Claude Code Instructions

## Story implementation workflow

When asked to implement a user story, always follow this sequence:

1. **@ai-engineer** — read the story from `planning/resume-tailoring-backlog.xlsx`, explore the codebase, and produce a written implementation plan (no code yet)
2. **@tech-lead** — review the plan; flag blockers before any code is written
3. **@ai-engineer** — incorporate tech-lead feedback, then implement on a feature branch named `s##-short-description`
4. **@ai-engineer** — open a PR
5. **@quality-analyst** — validate the implementation against the story's acceptance criteria, and add the QA report as a comment on the PR
6. **@ai-engineer** — fix any QA blockers, and comment on the PR to explain the fixes
7. **@tech-lead** — review the PR, and add any findings as a comment on the PR
8. **@ai-engineer** — address any tech-lead review comments, and comment on the PR to explain the fixes
9. **@tech-lead** — re-run the full test suite, verify fixes, then alert the human user that the PR is ready for final human review

After each step completes, post a short summary (2–4 bullet points) covering: what was done, any notable decisions or deviations, and what comes next.

Do not skip steps. Do not merge without human approval.

## PR format

Every PR description must include a **Manual validation** section with example shell commands a human can run to verify the feature end-to-end. Example:

````markdown
## Manual validation

```bash
echo "CV content" > /tmp/cv.txt
echo "JD content" > /tmp/jd.txt
EDITOR=cat uv run resume-tailor --cv /tmp/cv.txt --jd /tmp/jd.txt
# Expected: exits 0, outputs/YYYYMMDD_HHMMSS/resume.md created
```
````

The commands should be copy-pasteable and cover the happy path. Include expected output or observable side-effects so the reviewer knows what success looks like.

## Toolchain

- Package manager: `uv` — always use `uv sync --extra dev` to install
- Linting/formatting: `ruff` — run `uv run ruff check .` and `uv run ruff format --check .`
- Tests: `uv run pytest`
- Branch naming: `s##-short-description` (e.g. `s05-jd-extraction`)
