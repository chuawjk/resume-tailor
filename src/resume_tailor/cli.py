"""CLI entrypoint for resume-tailor."""

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume-tailor",
        description="Tailor a CV to a job description using an agentic workflow.",
    )
    parser.add_argument(
        "--cv",
        required=True,
        metavar="PATH",
        help="Path to the CV file (PDF or DOCX).",
    )
    parser.add_argument(
        "--jd",
        required=True,
        metavar="PATH",
        help="Path to the job description file.",
    )
    parser.add_argument(
        "--output",
        default="resume.md",
        metavar="PATH",
        help="Output path for the tailored resume (default: resume.md).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cv_path = Path(args.cv)
    jd_path = Path(args.jd)

    errors: list[str] = []
    if not cv_path.exists():
        errors.append(f"CV file not found: {cv_path}")
    if not jd_path.exists():
        errors.append(f"JD file not found: {jd_path}")

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1

    print("Not implemented: workflow not yet built.")
    return 0


def entrypoint() -> None:
    sys.exit(main())
