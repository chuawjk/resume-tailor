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

---

## Agent briefing standards

Each agent starts cold with no project context. Brief them with enough information to make good judgement calls, not just follow narrow instructions.

### Step 1 — @ai-engineer (plan)

Include in the brief:
- Full story row from the backlog: **all fields**, including Acceptance criteria, Non-goals, Dependencies, Evaluation approach, Notes
- Treat the **Evaluation approach** field as a required deliverable (e.g. an eval set must ship with the PR), not as metadata
- Instruct the engineer to **read existing agent and module implementations** before planning, to identify patterns they must follow (LLM client choice, error hierarchy shape, logging conventions, test structure)
- Ask them to explicitly call out any library or pattern decisions and justify them

### Step 2 — @tech-lead (plan review)

Include in the brief:
- The full plan from step 1
- The contents of `planning/resume-tailoring-architecture.md`
- An explicit instruction: **"Read the existing agent implementations and `workflow.py` to verify the plan is architecturally consistent with the rest of the codebase"**
- Ask: does this plan use the same LLM client, wrapper library, error hierarchy pattern, and logging approach as existing agents?

### Step 5 — @quality-analyst (QA)

Include in the brief:
- Full story row from the backlog: **all fields** (not just Acceptance criteria)
- Explicit instruction: **"Check for deliverables implied by the Evaluation approach, Notes, and Dependencies fields — not just the Acceptance criteria bullets"**
- Ask: is anything described in the backlog row missing from the implementation?

### Step 7 — @tech-lead (PR review)

Include in the brief:
- The PR diff and all prior PR comments
- An explicit instruction: **"Read the existing agent implementations and `workflow.py` to check for architectural consistency"** — does this PR follow the same patterns as the rest of the codebase?

---

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
