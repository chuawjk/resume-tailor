"""Unit tests for the Gap Analysis Agent.

All LLM calls are mocked — no network required.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from resume_tailor.agents.gap_analysis.agent import (
    Gap,
    GapAnalysis,
    GapAnalysisParseError,
    GapAnalysisValidationError,
    WeakMatch,
    analyse_gaps,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_GAP_ANALYSIS = GapAnalysis(
    strong_matches=["Python", "PostgreSQL"],
    weak_matches=[
        WeakMatch(
            requirement="Kubernetes",
            evidence="managed containerised apps in experience",
            user_note=None,
        )
    ],
    gaps=[Gap(requirement="GraphQL", acknowledged=False)],
)

SAMPLE_JD_PROFILE = {
    "role_title": "Backend Engineer",
    "seniority": "Senior",
    "hard_requirements": ["Python", "Kubernetes"],
    "nice_to_haves": ["GraphQL"],
    "culture_signals": [],
}

SAMPLE_CV_PROFILE = {
    "personal": {"name": "Jane Smith"},
    "skills": {"technical": ["Python", "PostgreSQL"], "domain": [], "soft": []},
    "experience": [
        {
            "role": "SWE",
            "organisation": "Acme",
            "start_date": "2019",
            "end_date": "Present",
            "responsibilities": ["managed containerised apps"],
            "achievements": [],
            "skills_demonstrated": [],
        }
    ],
    "education": [],
    "publications": [],
    "projects": [],
    "awards": [],
    "other": [],
}

# ValidationError instances for mocking
try:
    GapAnalysis.model_validate({"strong_matches": "not_a_list"})
except ValidationError as _e:
    _WRONG_TYPE_ERROR = _e

try:
    GapAnalysis.model_validate({"weak_matches": "not_a_list"})
except ValidationError as _e:
    _INVALID_WEAK_ERROR = _e

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
# Happy path — schema shape
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_returns_valid_schema(mock_openai_class: MagicMock) -> None:
    """analyse_gaps returns a dict with the three required top-level keys."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    result = analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    assert set(result.keys()) == {"strong_matches", "weak_matches", "gaps"}


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_strong_matches_are_strings(mock_openai_class: MagicMock) -> None:
    """strong_matches is a list of strings."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    result = analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    assert isinstance(result["strong_matches"], list)
    assert all(isinstance(s, str) for s in result["strong_matches"])


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_weak_matches_structure(mock_openai_class: MagicMock) -> None:
    """Each weak_match entry has requirement, evidence, and user_note keys."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    result = analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    for entry in result["weak_matches"]:
        assert "requirement" in entry
        assert "evidence" in entry
        assert "user_note" in entry


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_user_note_is_null_on_creation(mock_openai_class: MagicMock) -> None:
    """user_note is None on all weak_match entries produced by the agent."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    result = analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    for entry in result["weak_matches"]:
        assert entry["user_note"] is None


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_acknowledged_is_false_on_creation(mock_openai_class: MagicMock) -> None:
    """acknowledged is False on all gap entries produced by the agent."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    result = analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    for entry in result["gaps"]:
        assert entry["acknowledged"] is False


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_extra_fields_stripped(mock_openai_class: MagicMock) -> None:
    """model_config extra='ignore' ensures unexpected LLM fields never appear in output."""
    profile_with_extra = GapAnalysis.model_validate(
        {**VALID_GAP_ANALYSIS.model_dump(), "unexpected_field": "should be gone"}
    )
    mock_openai_class.return_value = _mock_llm(return_value=profile_with_extra)

    result = analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    assert "unexpected_field" not in result


# ---------------------------------------------------------------------------
# Temperature forwarding
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_temperature_passed_when_set(mock_openai_class: MagicMock) -> None:
    """temperature kwarg is forwarded to OpenAI constructor when explicitly set."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE, temperature=0.0)

    call_kwargs = mock_openai_class.call_args.kwargs
    assert "temperature" in call_kwargs
    assert call_kwargs["temperature"] == 0.0


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_temperature_not_passed_when_none(mock_openai_class: MagicMock) -> None:
    """temperature kwarg is NOT forwarded to OpenAI constructor when None."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    call_kwargs = mock_openai_class.call_args.kwargs
    assert "temperature" not in call_kwargs


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_raises_validation_error_on_schema_mismatch(
    mock_openai_class: MagicMock,
) -> None:
    """analyse_gaps raises GapAnalysisValidationError when fields have wrong types."""
    mock_openai_class.return_value = _mock_llm(side_effect=_WRONG_TYPE_ERROR)

    with pytest.raises(GapAnalysisValidationError):
        analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_raises_parse_error_on_unexpected_exception(
    mock_openai_class: MagicMock,
) -> None:
    """analyse_gaps raises GapAnalysisParseError when structured_predict raises unexpectedly."""
    mock_openai_class.return_value = _mock_llm(
        side_effect=ValueError("LLM returned unparseable content")
    )

    with pytest.raises(GapAnalysisParseError):
        analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_logs_info_on_start_and_completion(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """analyse_gaps emits INFO on start and completion."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.gap_analysis.agent"):
        analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    messages = [r.message for r in caplog.records]
    assert any("started" in m for m in messages), f"No 'started' log: {messages}"
    assert any("completed" in m for m in messages), f"No 'completed' log: {messages}"


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_logs_info_on_failure(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """analyse_gaps emits INFO with error type on failure."""
    mock_openai_class.return_value = _mock_llm(side_effect=_SAMPLE_VALIDATION_ERROR)

    with caplog.at_level(logging.INFO, logger="resume_tailor.agents.gap_analysis.agent"):
        with pytest.raises(GapAnalysisValidationError):
            analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    messages = [r.message for r in caplog.records]
    assert any("failed" in m for m in messages), f"No 'failed' log: {messages}"


@patch("resume_tailor.agents.gap_analysis.agent.OpenAI")
def test_analyse_gaps_logs_debug_prompt_and_result(
    mock_openai_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """analyse_gaps emits DEBUG logs for the prompt sent and the structured result."""
    mock_openai_class.return_value = _mock_llm(return_value=VALID_GAP_ANALYSIS)

    with caplog.at_level(logging.DEBUG, logger="resume_tailor.agents.gap_analysis.agent"):
        analyse_gaps(SAMPLE_JD_PROFILE, SAMPLE_CV_PROFILE)

    messages = [r.message for r in caplog.records]
    assert any("Prompt sent" in m for m in messages), f"No 'Prompt sent' DEBUG log: {messages}"
    assert any("Structured result" in m for m in messages), (
        f"No 'Structured result' DEBUG log: {messages}"
    )
