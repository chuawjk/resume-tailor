"""Fixtures for workflow integration tests.

The happy-path workflow test uses stub values for agents not yet fully implemented
(cv_extraction, gap_analysis, resume_tailoring, fabrication_judge) and mocks the
OpenAI call for jd_extraction so the test can run without credentials.
"""

import json
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
    """Mock the OpenAI client for jd_extraction so workflow tests don't need credentials."""
    with patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(_JD_PROFILE)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        yield
