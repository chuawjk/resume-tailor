"""Unit tests for the JD Extraction Agent.

All OpenAI API calls are mocked — no network required.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from resume_tailor.agents.jd_extraction.agent import (
    JDExtractionParseError,
    JDExtractionValidationError,
    extract_jd,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_JD_PROFILE = {
    "role_title": "Senior Software Engineer",
    "seniority": "Senior",
    "hard_requirements": ["5+ years Python", "PostgreSQL", "REST API design"],
    "nice_to_haves": ["Kubernetes", "GraphQL"],
    "culture_signals": ["fast-paced", "remote-first"],
}

SAMPLE_JD_TEXT = "We are hiring a Senior Software Engineer. 5+ years Python required."


def _make_mock_client(content: str) -> MagicMock:
    """Build a mock OpenAI client that returns *content* as the message content."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


# ---------------------------------------------------------------------------
# Test: schema validation of a well-formed response
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_returns_valid_schema(mock_openai_class: MagicMock) -> None:
    """extract_jd returns a dict matching the required schema for a well-formed response."""
    mock_openai_class.return_value = _make_mock_client(json.dumps(VALID_JD_PROFILE))

    result = extract_jd(SAMPLE_JD_TEXT)

    assert isinstance(result, dict)
    assert isinstance(result["role_title"], str)
    assert isinstance(result["seniority"], str)
    assert isinstance(result["hard_requirements"], list)
    assert isinstance(result["nice_to_haves"], list)
    assert isinstance(result["culture_signals"], list)

    # Confirm values were preserved
    assert result["role_title"] == "Senior Software Engineer"
    assert result["seniority"] == "Senior"
    assert "5+ years Python" in result["hard_requirements"]
    assert "Kubernetes" in result["nice_to_haves"]
    assert "fast-paced" in result["culture_signals"]


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_only_returns_required_keys(mock_openai_class: MagicMock) -> None:
    """extract_jd strips any extra keys returned by the LLM."""
    extra_fields = {**VALID_JD_PROFILE, "extra_field": "should be stripped"}
    mock_openai_class.return_value = _make_mock_client(json.dumps(extra_fields))

    result = extract_jd(SAMPLE_JD_TEXT)

    assert set(result.keys()) == {
        "role_title",
        "seniority",
        "hard_requirements",
        "nice_to_haves",
        "culture_signals",
    }
    assert "extra_field" not in result


# ---------------------------------------------------------------------------
# Test: error on malformed response (non-JSON)
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_raises_parse_error_on_non_json(mock_openai_class: MagicMock) -> None:
    """extract_jd raises JDExtractionParseError when the LLM returns non-JSON text."""
    mock_openai_class.return_value = _make_mock_client("Sorry, I cannot help with that.")

    with pytest.raises(JDExtractionParseError):
        extract_jd(SAMPLE_JD_TEXT)


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_raises_parse_error_on_json_array(mock_openai_class: MagicMock) -> None:
    """extract_jd raises JDExtractionValidationError when the LLM returns a JSON array."""
    mock_openai_class.return_value = _make_mock_client(json.dumps(["item1", "item2"]))

    with pytest.raises(JDExtractionValidationError, match="JSON object"):
        extract_jd(SAMPLE_JD_TEXT)


# ---------------------------------------------------------------------------
# Test: error on missing required fields
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_raises_validation_error_on_missing_fields(
    mock_openai_class: MagicMock,
) -> None:
    """extract_jd raises JDExtractionValidationError when required fields are absent."""
    partial_response = {"role_title": "Engineer"}
    mock_openai_class.return_value = _make_mock_client(json.dumps(partial_response))

    with pytest.raises(JDExtractionValidationError, match="missing required fields"):
        extract_jd(SAMPLE_JD_TEXT)


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_raises_validation_error_on_wrong_types(
    mock_openai_class: MagicMock,
) -> None:
    """extract_jd raises JDExtractionValidationError when fields have wrong types."""
    bad_types = {
        "role_title": "Engineer",
        "seniority": "Senior",
        "hard_requirements": "Python",  # should be list, not str
        "nice_to_haves": ["Kubernetes"],
        "culture_signals": ["fast-paced"],
    }
    mock_openai_class.return_value = _make_mock_client(json.dumps(bad_types))

    with pytest.raises(JDExtractionValidationError, match="wrong types"):
        extract_jd(SAMPLE_JD_TEXT)


# ---------------------------------------------------------------------------
# Test: logging
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_logs_info_on_start_and_completion(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_jd emits INFO log on start and on completion."""
    import logging

    mock_openai_class.return_value = _make_mock_client(json.dumps(VALID_JD_PROFILE))

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.jd_extraction.agent"):
        extract_jd(SAMPLE_JD_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("started" in m for m in messages), f"No 'started' log found in {messages}"
    assert any("completed" in m for m in messages), f"No 'completed' log found in {messages}"


@patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI")
def test_extract_jd_logs_info_on_failure(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_jd emits INFO log with error type on parse failure."""
    import logging

    mock_openai_class.return_value = _make_mock_client("not json")

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.jd_extraction.agent"):
        with pytest.raises(JDExtractionParseError):
            extract_jd(SAMPLE_JD_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("failed" in m for m in messages), f"No 'failed' log found in {messages}"
