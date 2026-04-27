"""Unit tests for the CV Extraction Agent.

All LLM calls are mocked — no network required.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from resume_tailor.agents.cv_extraction.agent import (
    CVExtractionParseError,
    CVExtractionValidationError,
    CVProfile,
    ExperienceEntry,
    PersonalInfo,
    SkillsSection,
    extract_cv,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_CV_PROFILE = CVProfile(
    personal=PersonalInfo(
        name="Jane Smith",
        email="jane@example.com",
        phone="+1-555-0100",
        location="San Francisco, CA",
        linkedin="linkedin.com/in/janesmith",
        website="janesmith.dev",
    ),
    education=[],
    experience=[
        ExperienceEntry(
            role="Senior Software Engineer",
            organisation="Acme Corp",
            start_date="Jan 2020",
            end_date="Present",
            responsibilities=["Designed REST APIs", "Led code reviews"],
            achievements=["Reduced latency by 30%"],
            skills_demonstrated=["Python", "PostgreSQL"],
        )
    ],
    publications=[],
    projects=[],
    awards=[],
    skills=SkillsSection(
        technical=["Python", "PostgreSQL", "Docker"],
        domain=["Backend Engineering"],
        soft=["communication", "leadership"],
    ),
    other=[],
)

SAMPLE_CV_TEXT = "Jane Smith\njane@example.com\nSenior Software Engineer at Acme Corp."

# ValidationError: wrong types on nested models.
try:
    CVProfile.model_validate({"personal": "not_a_dict"})
except ValidationError as _e:
    _WRONG_TYPE_ERROR = _e

# ValidationError: invalid nested data type.
try:
    CVProfile.model_validate({"experience": "not_a_list"})
except ValidationError as _e:
    _INVALID_LIST_ERROR = _e

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


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_returns_valid_schema(mock_openai_class: MagicMock) -> None:
    """extract_cv returns a dict with all required top-level keys."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    result = extract_cv(SAMPLE_CV_TEXT)

    assert set(result.keys()) == {
        "personal",
        "education",
        "experience",
        "publications",
        "projects",
        "awards",
        "skills",
        "other",
    }


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_personal_info_fields(mock_openai_class: MagicMock) -> None:
    """extract_cv returns correct personal info fields."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    result = extract_cv(SAMPLE_CV_TEXT)

    assert result["personal"]["name"] == "Jane Smith"
    assert result["personal"]["email"] == "jane@example.com"
    assert result["personal"]["phone"] == "+1-555-0100"
    assert result["personal"]["location"] == "San Francisco, CA"


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_experience_fields(mock_openai_class: MagicMock) -> None:
    """extract_cv returns correct experience entries."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    result = extract_cv(SAMPLE_CV_TEXT)

    assert len(result["experience"]) == 1
    exp = result["experience"][0]
    assert exp["role"] == "Senior Software Engineer"
    assert exp["organisation"] == "Acme Corp"
    assert exp["end_date"] == "Present"
    assert "Python" in exp["skills_demonstrated"]


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_skills_fields(mock_openai_class: MagicMock) -> None:
    """extract_cv returns correct skills sections."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    result = extract_cv(SAMPLE_CV_TEXT)

    assert "Python" in result["skills"]["technical"]
    assert "Backend Engineering" in result["skills"]["domain"]
    assert "communication" in result["skills"]["soft"]


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_extra_fields_stripped(mock_openai_class: MagicMock) -> None:
    """model_config extra='ignore' ensures extra LLM fields never appear in output."""
    profile_with_extra = CVProfile.model_validate(
        {**VALID_CV_PROFILE.model_dump(), "unexpected_field": "should be gone"}
    )
    mock_openai_class.return_value = _mock_llm(return_value=profile_with_extra)

    result = extract_cv(SAMPLE_CV_TEXT)

    assert "unexpected_field" not in result


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_absent_fields_use_empty_string_sentinel(mock_openai_class: MagicMock) -> None:
    """Absent scalar fields default to '' not None."""
    minimal_profile = CVProfile()
    mock_openai_class.return_value = _mock_llm(return_value=minimal_profile)

    result = extract_cv(SAMPLE_CV_TEXT)

    personal = result["personal"]
    assert personal["name"] == ""
    assert personal["email"] == ""
    assert personal["phone"] == ""
    assert personal["location"] == ""
    assert personal["linkedin"] == ""
    assert personal["website"] == ""
    # No None values in serialised output
    import json

    serialised = json.dumps(result)
    assert "null" not in serialised


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_temperature_passed_when_set(mock_openai_class: MagicMock) -> None:
    """temperature kwarg is forwarded to OpenAI constructor when explicitly set."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    extract_cv(SAMPLE_CV_TEXT, temperature=0.0)

    call_kwargs = mock_openai_class.call_args[1]
    assert "temperature" in call_kwargs
    assert call_kwargs["temperature"] == 0.0


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_temperature_not_passed_when_none(mock_openai_class: MagicMock) -> None:
    """temperature kwarg is NOT forwarded to OpenAI constructor when None."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    extract_cv(SAMPLE_CV_TEXT)

    call_kwargs = mock_openai_class.call_args[1]
    assert "temperature" not in call_kwargs


# ---------------------------------------------------------------------------
# Validation error (schema mismatch)
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_raises_validation_error_on_wrong_types(
    mock_openai_class: MagicMock,
) -> None:
    """extract_cv raises CVExtractionValidationError when fields have wrong types."""
    mock_openai_class.return_value = _mock_llm(side_effect=_WRONG_TYPE_ERROR)

    with pytest.raises(CVExtractionValidationError):
        extract_cv(SAMPLE_CV_TEXT)


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_raises_validation_error_on_invalid_list(
    mock_openai_class: MagicMock,
) -> None:
    """extract_cv raises CVExtractionValidationError when list fields have wrong types."""
    mock_openai_class.return_value = _mock_llm(side_effect=_INVALID_LIST_ERROR)

    with pytest.raises(CVExtractionValidationError):
        extract_cv(SAMPLE_CV_TEXT)


# ---------------------------------------------------------------------------
# Parse error (unexpected LLM failure)
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_raises_parse_error_on_unexpected_exception(
    mock_openai_class: MagicMock,
) -> None:
    """extract_cv raises CVExtractionParseError when structured_predict raises unexpectedly."""
    mock_openai_class.return_value = _mock_llm(
        side_effect=ValueError("LLM returned unparseable content")
    )

    with pytest.raises(CVExtractionParseError):
        extract_cv(SAMPLE_CV_TEXT)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_logs_info_on_start_and_completion(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_cv emits INFO on start and completion."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.cv_extraction.agent"):
        extract_cv(SAMPLE_CV_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("started" in m for m in messages), f"No 'started' log: {messages}"
    assert any("completed" in m for m in messages), f"No 'completed' log: {messages}"


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_logs_info_on_failure(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_cv emits INFO with error type on failure."""
    mock_openai_class.return_value = _mock_llm(side_effect=_SAMPLE_VALIDATION_ERROR)

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.cv_extraction.agent"):
        with pytest.raises(CVExtractionValidationError):
            extract_cv(SAMPLE_CV_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("failed" in m for m in messages), f"No 'failed' log: {messages}"


@patch("resume_tailor.agents.cv_extraction.agent.OpenAI")
def test_extract_cv_logs_debug_prompt_and_result(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """extract_cv emits DEBUG logs for the prompt sent and the structured result."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_CV_PROFILE)

    with caplog.at_level(logging.DEBUG, logger="resume_tailor.agents.cv_extraction.agent"):
        extract_cv(SAMPLE_CV_TEXT)

    messages = [r.message for r in caplog.records]
    assert any("Prompt sent" in m for m in messages), f"No 'Prompt sent' DEBUG log: {messages}"
    assert any("Structured result" in m for m in messages), (
        f"No 'Structured result' DEBUG log: {messages}"
    )
