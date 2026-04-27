"""Unit tests for jd_reader.read_jd()."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from resume_tailor.input_processing.jd_reader import (
    JDEncodingError,
    JDFileNotFoundError,
    JDPermissionError,
    JDUnsupportedFormatError,
    read_jd,
)

# Reuse the CV fixtures — same file formats, same content expectations.
FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "cvs"


# ---------------------------------------------------------------------------
# Happy-path tests for each supported format
# ---------------------------------------------------------------------------


def test_read_txt_happy_path():
    text = read_jd(FIXTURES / "sample.txt")
    assert "John Doe" in text
    assert len(text) > 0


def test_read_pdf_happy_path():
    text = read_jd(FIXTURES / "sample.pdf")
    assert "John Doe" in text
    assert len(text) > 0


def test_read_docx_happy_path():
    text = read_jd(FIXTURES / "sample.docx")
    assert "John Doe" in text
    assert len(text) > 0


def test_read_docx_includes_table_cells():
    """Table cell content must be included in extracted text."""
    text = read_jd(FIXTURES / "sample.docx")
    # sample.docx has a table with cells "Python" and "PostgreSQL"
    assert "Python" in text
    assert "PostgreSQL" in text


# ---------------------------------------------------------------------------
# Case-insensitive extension tests
# ---------------------------------------------------------------------------


def test_case_insensitive_pdf(tmp_path):
    dest = tmp_path / "jd.PDF"
    shutil.copy(FIXTURES / "sample.pdf", dest)
    text = read_jd(dest)
    assert "John Doe" in text


def test_case_insensitive_docx(tmp_path):
    dest = tmp_path / "jd.DOCX"
    shutil.copy(FIXTURES / "sample.docx", dest)
    text = read_jd(dest)
    assert "John Doe" in text


def test_case_insensitive_txt(tmp_path):
    dest = tmp_path / "jd.TXT"
    shutil.copy(FIXTURES / "sample.txt", dest)
    text = read_jd(dest)
    assert "John Doe" in text


def test_mixed_case_extension(tmp_path):
    dest = tmp_path / "jd.Pdf"
    shutil.copy(FIXTURES / "sample.pdf", dest)
    text = read_jd(dest)
    assert "John Doe" in text


# ---------------------------------------------------------------------------
# String path support
# ---------------------------------------------------------------------------


def test_accepts_string_path():
    """read_jd must accept a plain string, not just a Path object."""
    text = read_jd(str(FIXTURES / "sample.txt"))
    assert "John Doe" in text


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unsupported_extension_raises_error(tmp_path):
    f = tmp_path / "jd.xyz"
    f.write_text("some content")
    with pytest.raises(JDUnsupportedFormatError) as exc_info:
        read_jd(f)
    msg = str(exc_info.value).lower()
    assert ".pdf" in msg
    assert ".docx" in msg
    assert ".txt" in msg


def test_unsupported_extension_message_names_extension(tmp_path):
    f = tmp_path / "jd.odt"
    f.write_text("some content")
    with pytest.raises(JDUnsupportedFormatError) as exc_info:
        read_jd(f)
    assert ".odt" in str(exc_info.value)


def test_unsupported_extension_checked_before_existence():
    """Extension check must fire even when the file does not exist."""
    with pytest.raises(JDUnsupportedFormatError):
        read_jd("/nonexistent/path/jd.xyz")


def test_missing_file_raises_error():
    with pytest.raises(JDFileNotFoundError) as exc_info:
        read_jd("/nonexistent/path/jd.txt")
    assert "/nonexistent/path/jd.txt" in str(exc_info.value)


def test_missing_pdf_file_raises_error(tmp_path):
    with pytest.raises(JDFileNotFoundError):
        read_jd(tmp_path / "does_not_exist.pdf")


def test_encoding_error_on_non_utf8_txt(tmp_path):
    """A file with latin-1 bytes must raise JDEncodingError, not silently corrupt."""
    f = tmp_path / "latin1.txt"
    # Write bytes that are valid latin-1 but not valid UTF-8
    f.write_bytes(b"Job Description for Jos\xe9\n")
    with pytest.raises(JDEncodingError) as exc_info:
        read_jd(f)
    assert str(f) in str(exc_info.value)


def test_permission_error_raises_jd_permission_error(tmp_path, monkeypatch):
    """PermissionError from the OS must be wrapped as JDPermissionError."""
    f = tmp_path / "jd.txt"
    f.write_text("some content")

    import resume_tailor.input_processing.jd_reader as _jdr

    monkeypatch.setattr(
        _jdr, "read_txt", lambda p: (_ for _ in ()).throw(PermissionError("denied"))
    )
    with pytest.raises(JDPermissionError) as exc_info:
        read_jd(f)
    assert str(f) in str(exc_info.value)
