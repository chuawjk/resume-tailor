"""Logging configuration for resume-tailor."""

import logging
import sys


def configure_logging(log_file: str, log_level: str) -> None:
    """Configure root logger with a stdout handler and a file handler.

    Args:
        log_file: Path to the log file.
        log_level: Log level string for the stdout handler (e.g. "INFO").
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level!r}")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(numeric_level)
    stdout_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s"))

    root.addHandler(stdout_handler)
    root.addHandler(file_handler)
