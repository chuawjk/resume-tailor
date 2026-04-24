"""Unit tests for logging_config.configure_logging."""

import logging

import pytest

from resume_tailor.logging_config import configure_logging


@pytest.fixture(autouse=True)
def reset_root_logger():
    """Snapshot the root logger state, clear non-pytest handlers, then restore after the test."""
    # Separate pytest-internal handlers (LogCaptureHandler) from user-land handlers.
    pytest_handlers = [h for h in logging.root.handlers if type(h).__name__ == "LogCaptureHandler"]
    original_level = logging.root.level

    # Remove any user-land handlers accumulated by previous tests so each test starts clean.
    for handler in list(logging.root.handlers):
        if type(handler).__name__ != "LogCaptureHandler":
            handler.close()
            logging.root.removeHandler(handler)

    yield

    # Teardown: remove user-land handlers added during this test.
    for handler in list(logging.root.handlers):
        if type(handler).__name__ != "LogCaptureHandler":
            handler.close()
            logging.root.removeHandler(handler)

    # Restore the level in case configure_logging changed it.
    logging.root.setLevel(original_level)

    # Re-attach any pytest handlers that were inadvertently removed.
    for handler in pytest_handlers:
        if handler not in logging.root.handlers:
            logging.root.addHandler(handler)


def _our_handlers() -> list[logging.Handler]:
    """Return only the StreamHandler and FileHandler added by configure_logging.

    Pytest injects its own LogCaptureHandler instances; exclude those so the
    counts and level assertions are not polluted by pytest internals.
    """
    return [h for h in logging.root.handlers if type(h).__name__ not in ("LogCaptureHandler",)]


def test_configure_logging_attaches_two_handlers(tmp_path):
    log_file = str(tmp_path / "test.log")
    configure_logging(log_file, "INFO")
    assert len(_our_handlers()) == 2


def test_configure_logging_stdout_handler_level(tmp_path):
    log_file = str(tmp_path / "test.log")
    configure_logging(log_file, "INFO")
    stream_handlers = [
        h
        for h in _our_handlers()
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
    ]
    assert len(stream_handlers) == 1
    assert stream_handlers[0].level == logging.INFO


def test_configure_logging_file_handler_level(tmp_path):
    log_file = str(tmp_path / "test.log")
    configure_logging(log_file, "INFO")
    file_handlers = [h for h in _our_handlers() if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
    assert file_handlers[0].level == logging.DEBUG


def test_configure_logging_file_handler_format_contains_module(tmp_path):
    log_file = str(tmp_path / "test.log")
    configure_logging(log_file, "INFO")
    file_handlers = [h for h in _our_handlers() if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
    assert "%(module)s" in file_handlers[0].formatter._fmt
