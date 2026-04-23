# Contributing

## Setup

```bash
uv sync --extra dev
pre-commit install
```

Copy `.env.example` to `.env` and fill in your `OPENAI_API_KEY`.

## Project structure

```
src/resume_tailor/
    cli.py                  # CLI entrypoint
    agents/
        jd_extraction/      # Parses job description into structured profile
        cv_extraction/      # Parses CV into structured profile
        gap_analysis/       # Compares JD requirements against CV profile
        resume_tailoring/   # Rewrites CV content targeting the JD
        fabrication_judge/  # Verifies tailored resume claims against CV
tests/
    unit/                   # Fast, isolated tests — mirror src/ structure
    integration/            # End-to-end tests — mirror src/ structure
```

Each agent directory contains:
- `agent.py` — agent logic
- `prompts.py` — prompt templates
- `__init__.py`

## Development workflow

Run tests:
```bash
uv run pytest
```

Lint and format:
```bash
uv run ruff check --fix .
uv run ruff format .
```

Pre-commit runs both ruff and pytest automatically on `git commit`.

## Adding a new agent

1. Create a subdir under `src/resume_tailor/agents/` with `__init__.py`, `agent.py`, `prompts.py`.
2. Add corresponding test dirs under `tests/unit/agents/` and `tests/integration/agents/`.

## Branching

Work on feature branches. Branch names should reference the story ID: `s02-logging`, `s03-jd-extraction`, etc.
