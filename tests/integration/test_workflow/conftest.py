"""Fixtures for workflow integration tests.

The happy-path workflow test uses stub values for agents not yet fully implemented
(cv_extraction, gap_analysis, resume_tailoring, fabrication_judge) and mocks the
OpenAI call for jd_extraction so the test can run without credentials.
"""

from unittest.mock import MagicMock, patch

import pytest

_JD_PROFILE = {
    "role_title": "Senior Software Engineer",
    "seniority": "Senior",
    "hard_requirements": ["Python", "REST APIs", "PostgreSQL"],
    "nice_to_haves": ["Kubernetes", "GraphQL"],
    "culture_signals": ["fast-paced", "collaborative"],
}


@pytest.fixture(autouse=True)
def mock_jd_extraction_openai():
    """Mock the LlamaIndex OpenAI LLM for jd_extraction so workflow tests don't need credentials."""
    from resume_tailor.agents.jd_extraction.agent import JDProfile

    with patch("resume_tailor.agents.jd_extraction.agent.OpenAI") as mock_openai_class:
        mock_llm = MagicMock()
        mock_llm.structured_predict.return_value = JDProfile(**_JD_PROFILE)
        mock_openai_class.return_value = mock_llm
        yield
