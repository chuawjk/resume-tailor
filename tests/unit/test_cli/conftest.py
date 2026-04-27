"""Fixtures for CLI unit tests.

All agent functions are mocked so that CLI tests don't make real API calls.
This conftest was added when S06 replaced the JD extraction stub with a real
OpenAI call, which broke existing CLI unit tests that relied on the stub returning
hardcoded data.
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

_CV_PROFILE = {
    "personal": {"name": "Jane Smith", "email": "jane@example.com"},
    "education": [],
    "experience": [],
    "publications": [],
    "projects": [],
    "awards": [],
    "skills": {"technical": [], "domain": [], "soft": []},
    "other": [],
}


@pytest.fixture(autouse=True)
def mock_agents():
    """Auto-mock all agent functions to prevent real API calls in CLI unit tests."""
    with (
        patch("resume_tailor.agents.jd_extraction.agent.openai.OpenAI") as mock_openai_class,
        patch(
            "resume_tailor.agents.cv_extraction.agent.extract_cv",
            return_value=_CV_PROFILE,
        ),
        patch(
            "resume_tailor.agents.gap_analysis.agent.analyse_gaps",
            return_value={"gaps": [], "matches": []},
        ),
        patch(
            "resume_tailor.agents.resume_tailoring.agent.tailor_resume",
            return_value="# Tailored Resume\n\nContent here.",
        ),
        patch(
            "resume_tailor.agents.fabrication_judge.agent.judge_fabrication",
            return_value={"verdict": "pass", "issues": []},
        ),
    ):
        import json

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(_JD_PROFILE)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        yield
