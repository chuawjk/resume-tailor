# resume-tailor

An agentic CLI workflow that takes a CV and job description, runs them through
a series of LLM-powered agents with human review checkpoints, and produces a
tailored resume as a Markdown file.

## Workflow

```
CV file + JD file
        |
   ┌────┴────┐
   ↓         ↓
[JD         [CV
 Extraction  Extraction
 Agent]      Agent]
   ↓         ↓
Job Profile  CV Profile
   └────┬────┘
        ↓
  ⬡ CHECKPOINT 1
    Review profiles in $EDITOR
        ↓
  [Gap Analysis Agent]
        ↓
  ⬡ CHECKPOINT 2
    Review gap analysis in $EDITOR
        ↓
  [Resume Tailoring Agent]
        ↓
  [Fabrication Judge Agent]
        ↓
  ⬡ CHECKPOINT 3
    Review resume + fabrication report in $EDITOR
        ↓
     resume.md
```

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
uv sync --extra dev
```

## Development setup

After installing, set up the pre-commit hooks (runs ruff and pytest on every commit):

```bash
pre-commit install
```

To run the hooks manually against all files:

```bash
pre-commit run --all-files
```

## Basic invocation

```bash
resume-tailor --cv path/to/cv.pdf --jd path/to/job_description.txt
```

By default the output is written to `resume.md` in the current directory.
Use `--output` to specify a different path:

```bash
resume-tailor --cv cv.pdf --jd jd.txt --output tailored_resume.md
```

## Running tests

```bash
pytest
```

## Linting and formatting

```bash
ruff check .        # lint
ruff check --fix .  # lint with auto-fix
ruff format .       # format
```
