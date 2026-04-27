"""CLI entrypoint for resume-tailor."""

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from resume_tailor.editor import edit_in_editor
from resume_tailor.input_processing.cv_reader import CVReaderError, read_cv
from resume_tailor.logging_config import configure_logging
from resume_tailor.workflow import (
    Checkpoint1RequestEvent,
    Checkpoint1ResponseEvent,
    Checkpoint2RequestEvent,
    Checkpoint2ResponseEvent,
    Checkpoint3RequestEvent,
    Checkpoint3ResponseEvent,
    ResumeStartEvent,
    ResumeWorkflow,
)

try:
    from llama_index.core.workflow import WorkflowFailedEvent
except ImportError:
    try:
        from workflows.events import WorkflowFailedEvent  # type: ignore[no-redef]
    except ImportError:
        WorkflowFailedEvent = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

FABRICATION_SENTINEL_START = "<!-- FABRICATION_REPORT_START -->"
FABRICATION_SENTINEL_END = "<!-- FABRICATION_REPORT_END -->"


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
        "--output",
        default=None,
        metavar="PATH",
        help="Path for the final resume output (default: <output-dir>/<run>/resume.md).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO).",
    )
    return parser


async def run_workflow(cv_text: str, jd_text: str, output_path: Path) -> None:
    """Run the resume-tailoring workflow with human checkpoints."""
    print("[1/3] Extracting profiles...")

    workflow = ResumeWorkflow(timeout=None)
    handler = workflow.run(start_event=ResumeStartEvent(cv_text=cv_text, jd_text=jd_text))

    async for event in handler.stream_events():
        if WorkflowFailedEvent is not None and isinstance(event, WorkflowFailedEvent):
            raise RuntimeError(
                f"Workflow failed at step '{event.step_name}': {event.exception_message}"
            )

        elif isinstance(event, Checkpoint1RequestEvent):
            print("      ✓ JD profile extracted")
            print("      ✓ CV profile extracted")
            print()
            print("      Opening profiles in $EDITOR for review...")
            print("      Press Enter when done.")
            print()

            combined = {
                "jd_profile": event.jd_profile,
                "cv_profile": event.cv_profile,
            }
            json_str = json.dumps(combined, indent=2)

            logger.info("Checkpoint 1: opening editor")
            edited_str = await asyncio.to_thread(edit_in_editor, json_str, ".json")

            if edited_str == json_str:
                logger.info("Checkpoint 1: content unchanged")
            else:
                logger.info("Checkpoint 1: content edited by user")

            try:
                edited_data = json.loads(edited_str)
                jd_profile = edited_data.get("jd_profile", event.jd_profile)
                cv_profile = edited_data.get("cv_profile", event.cv_profile)
            except json.JSONDecodeError:
                logger.warning("Checkpoint 1: JSON parse error; using original profiles")
                jd_profile = event.jd_profile
                cv_profile = event.cv_profile

            await handler.send_event(
                Checkpoint1ResponseEvent(jd_profile=jd_profile, cv_profile=cv_profile)
            )

        elif isinstance(event, Checkpoint2RequestEvent):
            print("[2/3] Running gap analysis...")
            print("      ✓ Gap analysis complete")
            print()
            print("      Opening gap analysis in $EDITOR for review...")
            print("      Press Enter when done.")
            print()

            json_str = json.dumps(event.gap_analysis, indent=2)

            logger.info("Checkpoint 2: opening editor")
            edited_str = await asyncio.to_thread(edit_in_editor, json_str, ".json")

            if edited_str == json_str:
                logger.info("Checkpoint 2: content unchanged")
            else:
                logger.info("Checkpoint 2: content edited by user")

            try:
                gap_analysis = json.loads(edited_str)
            except json.JSONDecodeError:
                logger.warning("Checkpoint 2: JSON parse error; using original gap analysis")
                gap_analysis = event.gap_analysis

            await handler.send_event(Checkpoint2ResponseEvent(gap_analysis=gap_analysis))

        elif isinstance(event, Checkpoint3RequestEvent):
            print("[3/3] Tailoring resume...")
            print("      ✓ Resume drafted")

            report = event.fabrication_report
            overall = report.get("overall_assessment", "clean")
            verdicts = report.get("verdicts", [])
            print(f"      ✓ Fabrication check complete: {overall}")
            if verdicts:
                print(f"        ⚠ {len(verdicts)} claims flagged for review")

            print()
            print("      Opening resume and fabrication report in $EDITOR for review...")
            print("      Press Enter when done.")
            print()

            combined = (
                f"{event.tailored_resume}\n\n"
                f"{FABRICATION_SENTINEL_START}\n"
                f"{json.dumps(report, indent=2)}\n"
                f"{FABRICATION_SENTINEL_END}"
            )

            logger.info("Checkpoint 3: opening editor")
            edited = await asyncio.to_thread(edit_in_editor, combined, ".md")

            if edited == combined:
                logger.info("Checkpoint 3: content unchanged")
            else:
                logger.info("Checkpoint 3: content edited by user")

            pattern = re.compile(
                r"\n*"
                + re.escape(FABRICATION_SENTINEL_START)
                + r".*?"
                + re.escape(FABRICATION_SENTINEL_END)
                + r"\n*",
                re.DOTALL,
            )
            match = pattern.search(edited)
            if not match:
                logger.warning(
                    "Fabrication report sentinel not found in edited content; using as-is"
                )
                final = edited.strip()
            else:
                final = pattern.sub("", edited).strip()

            await handler.send_event(Checkpoint3ResponseEvent(final_resume=final))

    final_resume = await handler
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_resume, encoding="utf-8")


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

    output_path = Path(args.output) if args.output else run_dir / "resume.md"
    try:
        cv_text = read_cv(cv_path)
    except CVReaderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    jd_text = jd_path.read_text(encoding="utf-8")
    asyncio.run(run_workflow(cv_text, jd_text, output_path))
    print(f"\nSaved to {output_path}")
    return 0


def entrypoint() -> None:
    sys.exit(main())
