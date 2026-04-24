"""CLI entrypoint for resume-tailor."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from resume_tailor.logging_config import configure_logging


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
        "--output-dir",
        default="outputs",
        metavar="DIR",
        help="Base directory for all outputs (default: outputs/).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    run_dir = Path(args.output_dir) / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    configure_logging(str(run_dir / "resume-tailor.log"), args.log_level)

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
