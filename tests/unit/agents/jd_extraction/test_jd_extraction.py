"""Unit tests for the JD Extraction Agent.

All LLM calls are mocked — no network required.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from resume_tailor.agents.jd_extraction.agent import (
    JDExtractionParseError,
    JDExtractionValidationError,
    JDProfile,
    extract_jd,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_JD_PROFILE = JDProfile(
    role_title="Senior Software Engineer",
    seniority="Senior",
    hard_requirements=["5+ years Python", "PostgreSQL", "REST API design"],
    nice_to_haves=["Kubernetes", "GraphQL"],
    culture_signals=["fast-paced", "remote-first"],
)

SAMPLE_JD_TEXT = "We are hiring a Senior Software Engineer. 5+ years Python required."

# ValidationError: wrong types on existing fields.
try:
    JDProfile.model_validate({"role_title": 123, "seniority": None})
except ValidationError as _e:
    _WRONG_TYPE_ERROR = _e

# ValidationError: missing required fields.
try:
    JDProfile.model_validate({"role_title": "Engineer"})
except ValidationError as _e:
    _MISSING_FIELDS_ERROR = _e

_SAMPLE_VALIDATION_ERROR = _WRONG_TYPE_ERROR


def _mock_llm(return_value=None, side_effect=None) -> MagicMock:
    """Return a mock LlamaIndex LLM whose structured_predict is configured."""
    mock = MagicMock()
    if side_effect is not None:
        mock.structured_predict.side_effect = side_effect
    else:
        mock.structured_predict.return_value = return_value
    return mock


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_returns_valid_schema(mock_openai_class: MagicMock) -> None:
    """extract_jd returns a dict matching the required schema."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_JD_PROFILE)

    result = extract_jd(SAMPLE_JD_TEXT)

    assert set(result.keys()) == {
        "role_title",
        "seniority",
        "hard_requirements",
        "nice_to_haves",
        "culture_signals",
    }
    assert result["role_title"] == "Senior Software Engineer"
    assert result["seniority"] == "Senior"
    assert "5+ years Python" in result["hard_requirements"]
    assert "Kubernetes" in result["nice_to_haves"]
    assert "fast-paced" in result["culture_signals"]


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_extra_fields_stripped(mock_openai_class: MagicMock) -> None:
    """model_config extra='ignore' ensures extra LLM fields never appear in output."""
    profile_with_extra = JDProfile.model_validate(
        {**VALID_JD_PROFILE.model_dump(), "unexpected_field": "should be gone"}
    )
    mock_openai_class.return_value = _mock_llm(return_value=profile_with_extra)

    result = extract_jd(SAMPLE_JD_TEXT)

    assert "unexpected_field" not in result
    assert set(result.keys()) == {
        "role_title",
        "seniority",
        "hard_requirements",
        "nice_to_haves",
        "culture_signals",
    }


# ---------------------------------------------------------------------------
# Validation error (schema mismatch)
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_raises_validation_error_on_wrong_types(
    mock_openai_class: MagicMock,
) -> None:
    """extract_jd raises JDExtractionValidationError when fields have wrong types."""
    mock_openai_class.return_value = _mock_llm(side_effect=_WRONG_TYPE_ERROR)

    with pytest.raises(JDExtractionValidationError):
        extract_jd(SAMPLE_JD_TEXT)


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_raises_validation_error_on_missing_fields(
    mock_openai_class: MagicMock,
) -> None:
    """extract_jd raises JDExtractionValidationError when required fields are absent."""
    mock_openai_class.return_value = _mock_llm(side_effect=_MISSING_FIELDS_ERROR)

    with pytest.raises(JDExtractionValidationError):
        extract_jd(SAMPLE_JD_TEXT)


# ---------------------------------------------------------------------------
# Parse error (unexpected LLM failure)
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_raises_parse_error_on_unexpected_exception(
    mock_openai_class: MagicMock,
) -> None:
    """extract_jd raises JDExtractionParseError when structured_predict raises unexpectedly."""
    mock_openai_class.return_value = _mock_llm(
        side_effect=ValueError("LLM returned unparseable content")
    )

    with pytest.raises(JDExtractionParseError):
        extract_jd(SAMPLE_JD_TEXT)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_logs_info_on_start_and_completion(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_jd emits INFO on start and completion."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_JD_PROFILE)

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.jd_extraction.agent"):
        extract_jd(SAMPLE_JD_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("started" in m for m in messages), f"No 'started' log: {messages}"
    assert any("completed" in m for m in messages), f"No 'completed' log: {messages}"


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_logs_info_on_failure(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_jd emits INFO with error type on failure."""
    mock_openai_class.return_value = _mock_llm(side_effect=_SAMPLE_VALIDATION_ERROR)

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.jd_extraction.agent"):
        with pytest.raises(JDExtractionValidationError):
            extract_jd(SAMPLE_JD_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("failed" in m for m in messages), f"No 'failed' log: {messages}"


@patch("resume_tailor.agents.jd_extraction.agent.OpenAI")
def test_extract_jd_logs_debug_prompt_and_result(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_jd emits DEBUG logs for the prompt sent and the structured result."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_JD_PROFILE)

    with caplog.at_level(logging.DEBUG, logger="resume_tailor.agents.jd_extraction.agent"):
        extract_jd(SAMPLE_JD_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("Prompt sent" in m for m in messages), f"No 'Prompt sent' DEBUG log: {messages}"
    assert any("Structured result" in m for m in messages), (
        f"No 'Structured result' DEBUG log: {messages}"
    )
