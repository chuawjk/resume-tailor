"""JD reader — extracts raw text from PDF, DOCX, and plain-text job description files."""

from __future__ import annotations

from pathlib import Path

from resume_tailor.input_processing._file_reader import (
    SUPPORTED_EXTENSIONS,
    read_docx,
    read_pdf,
    read_txt,
)

__all__ = [
    "read_jd",
    "JDReaderError",
    "JDFileNotFoundError",
    "JDPermissionError",
    "JDUnsupportedFormatError",
    "JDEncodingError",
    "SUPPORTED_EXTENSIONS",
]


# ---------------------------------------------------------------------------
# Typed error hierarchy
# ---------------------------------------------------------------------------


class JDReaderError(Exception):
    """Base class for all JD reader errors."""


class JDFileNotFoundError(JDReaderError):
    """Raised when the JD file does not exist.

    Note: does not subclass the built-in ``FileNotFoundError`` by design —
    callers should catch ``JDReaderError`` or ``JDFileNotFoundError`` explicitly.
    """


class JDPermissionError(JDReaderError):
    """Raised when the JD file cannot be read due to a permission error."""


class JDUnsupportedFormatError(JDReaderError):
    """Raised when the file extension is not supported."""


class JDEncodingError(JDReaderError):
    """Raised when a plain-text file cannot be decoded as UTF-8."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def read_jd(path: str | Path) -> str:
    """Read a job description file and return its raw text content.

    Dispatches on the file extension (case-insensitive):
    - ``.pdf``  — extracted via pdfplumber
    - ``.docx`` — extracted via python-docx (paragraphs + table cells)
    - ``.txt``  — read as UTF-8

    Extension check is performed first, then existence check — matching the
    behaviour of ``read_cv``.

    Raises:
        JDFileNotFoundError: If the file does not exist.
        JDPermissionError: If the file cannot be read due to OS permissions.
        JDUnsupportedFormatError: If the extension is not one of the supported
            formats (.pdf, .docx, .txt).
        JDEncodingError: If a .txt file contains non-UTF-8 bytes.
    """
    path = Path(path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(SUPPORTED_EXTENSIONS)
        raise JDUnsupportedFormatError(
            f"Unsupported file format {path.suffix!r}. Supported formats: {supported}"
        )

    if not path.exists():
        raise JDFileNotFoundError(f"JD file not found: {path}")

    try:
        if ext == ".pdf":
            return read_pdf(path)
        elif ext == ".docx":
            return read_docx(path)
        else:
            try:
                return read_txt(path)
            except UnicodeDecodeError as exc:
                raise JDEncodingError(
                    f"JD file is not valid UTF-8: {path}. "
                    "Ensure the file is saved with UTF-8 encoding."
                ) from exc
    except PermissionError as exc:
        raise JDPermissionError(f"Permission denied reading JD file: {path}") from exc
