"""Unit tests for cv_reader.read_cv()."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from resume_tailor.input_processing.cv_reader import (
    CVEncodingError,
    CVFileNotFoundError,
    CVUnsupportedFormatError,
    read_cv,
)

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "cvs"


# ---------------------------------------------------------------------------
# Happy-path tests for each supported format
# ---------------------------------------------------------------------------


def test_read_txt_happy_path():
    text = read_cv(FIXTURES / "sample.txt")
    assert "John Doe" in text
    assert len(text) > 0


def test_read_pdf_happy_path():
    text = read_cv(FIXTURES / "sample.pdf")
    assert "John Doe" in text
    assert len(text) > 0


def test_read_docx_happy_path():
    text = read_cv(FIXTURES / "sample.docx")
    assert "John Doe" in text
    assert len(text) > 0


def test_read_docx_includes_table_cells():
    """Table cell content must be included in extracted text."""
    text = read_cv(FIXTURES / "sample.docx")
    # sample.docx has a table with cells "Python" and "PostgreSQL"
    assert "Python" in text
    assert "PostgreSQL" in text


# ---------------------------------------------------------------------------
# Case-insensitive extension tests
# ---------------------------------------------------------------------------


def test_case_insensitive_pdf(tmp_path):
    dest = tmp_path / "cv.PDF"
    shutil.copy(FIXTURES / "sample.pdf", dest)
    text = read_cv(dest)
    assert "John Doe" in text


def test_case_insensitive_docx(tmp_path):
    dest = tmp_path / "cv.DOCX"
    shutil.copy(FIXTURES / "sample.docx", dest)
    text = read_cv(dest)
    assert "John Doe" in text


def test_case_insensitive_txt(tmp_path):
    dest = tmp_path / "cv.TXT"
    shutil.copy(FIXTURES / "sample.txt", dest)
    text = read_cv(dest)
    assert "John Doe" in text


def test_mixed_case_extension(tmp_path):
    dest = tmp_path / "cv.Pdf"
    shutil.copy(FIXTURES / "sample.pdf", dest)
    text = read_cv(dest)
    assert "John Doe" in text


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unsupported_extension_raises_error(tmp_path):
    f = tmp_path / "cv.xyz"
    f.write_text("some content")
    with pytest.raises(CVUnsupportedFormatError) as exc_info:
        read_cv(f)
    msg = str(exc_info.value).lower()
    assert ".pdf" in msg
    assert ".docx" in msg
    assert ".txt" in msg


def test_unsupported_extension_message_names_extension(tmp_path):
    f = tmp_path / "cv.odt"
    f.write_text("some content")
    with pytest.raises(CVUnsupportedFormatError) as exc_info:
        read_cv(f)
    assert ".odt" in str(exc_info.value)


def test_missing_file_raises_error():
    with pytest.raises(CVFileNotFoundError) as exc_info:
        read_cv("/nonexistent/path/cv.txt")
    assert "/nonexistent/path/cv.txt" in str(exc_info.value)


def test_missing_pdf_file_raises_error(tmp_path):
    with pytest.raises(CVFileNotFoundError):
        read_cv(tmp_path / "does_not_exist.pdf")


def test_encoding_error_on_non_utf8_txt(tmp_path):
    """A file with latin-1 bytes must raise CVEncodingError, not silently corrupt."""
    f = tmp_path / "latin1.txt"
    # Write bytes that are valid latin-1 but not valid UTF-8
    f.write_bytes(b"R\xe9sum\xe9 of Jos\xe9\n")
    with pytest.raises(CVEncodingError) as exc_info:
        read_cv(f)
    assert str(f) in str(exc_info.value)


# ---------------------------------------------------------------------------
# String path support
# ---------------------------------------------------------------------------


def test_accepts_string_path():
    """read_cv must accept a plain string, not just a Path object."""
    text = read_cv(str(FIXTURES / "sample.txt"))
    assert "John Doe" in text
