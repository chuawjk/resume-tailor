"""Integration test for the JD Extraction Agent.

Makes one real OpenAI API call. Requires OPENAI_API_KEY to be set.
Skipped automatically in CI environments without credentials.

Run with:
    OPENAI_API_KEY=sk-... uv run pytest tests/integration/agents/jd_extraction/ -v
"""

import os

import pytest

from resume_tailor.agents.jd_extraction.agent import extract_jd

# ---------------------------------------------------------------------------
# Fixture JD — realistic corporate posting with boilerplate, DEI, and legal text
# ---------------------------------------------------------------------------

FIXTURE_JD = """\
About Acme Corp
===============
Acme Corp is a leading provider of cloud-based software solutions serving Fortune 500 clients
worldwide. Founded in 2010, we have grown to over 2,000 employees across 12 countries. We are
passionate about innovation, customer success, and our dynamic team culture.

The Role: Senior Backend Engineer
==================================
We are seeking a talented Senior Backend Engineer to join our Platform team. You will be
responsible for designing and scaling our core API infrastructure to support our next phase
of growth.

What you MUST have (Required):
- 5+ years of professional software engineering experience
- 4+ years of experience with Python (3.8+)
- Strong experience designing and building REST APIs
- Proficiency with PostgreSQL or another relational database
- Experience with distributed systems and microservices architecture
- Bachelor's degree in Computer Science or equivalent practical experience

What would be nice to have (Bonus points):
- Experience with Kubernetes and Docker in production environments
- Familiarity with GraphQL APIs
- Exposure to event-driven architectures (Kafka, RabbitMQ) would be a plus
- We would love someone who has worked with dbt or similar data transformation tools

About our culture:
- Fast-paced startup environment despite our size
- Remote-first — you can work from anywhere
- Flat hierarchy — engineers talk directly to product and leadership
- Collaborative, low-ego team

What we offer:
- Competitive salary ($150k–$200k depending on experience)
- Comprehensive health, dental, and vision insurance
- 401(k) with 4% company match
- Generous PTO and parental leave
- Home office stipend

Equal Opportunity Employer
==========================
Acme Corp is an Equal Opportunity Employer. We celebrate diversity and are committed to
creating an inclusive environment for all employees. We do not discriminate on the basis of
race, religion, color, national origin, gender, sexual orientation, age, marital status,
veteran status, or disability status.

Candidates must be authorized to work in the United States. Acme Corp does not provide
visa sponsorship for this position. A background check will be required upon offer of
employment.
"""


# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_extract_jd_real_api_call() -> None:
    """Make a real API call and verify the response matches the expected schema."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — skipping integration test")

    result = extract_jd(FIXTURE_JD)

    # Schema validation
    assert isinstance(result, dict), "Result should be a dict"
    assert set(result.keys()) == {
        "role_title",
        "seniority",
        "hard_requirements",
        "nice_to_haves",
        "culture_signals",
    }, f"Unexpected keys: {set(result.keys())}"

    assert isinstance(result["role_title"], str) and result["role_title"], (
        "role_title must be a non-empty string"
    )
    assert isinstance(result["seniority"], str) and result["seniority"], (
        "seniority must be a non-empty string"
    )
    assert isinstance(result["hard_requirements"], list), "hard_requirements must be a list"
    assert isinstance(result["nice_to_haves"], list), "nice_to_haves must be a list"
    assert isinstance(result["culture_signals"], list), "culture_signals must be a list"

    # Content sanity checks
    role_lower = result["role_title"].lower()
    assert "engineer" in role_lower, (
        f"Expected 'engineer' in role_title, got {result['role_title']!r}"
    )

    seniority_lower = result["seniority"].lower()
    assert "senior" in seniority_lower, (
        f"Expected 'senior' in seniority, got {result['seniority']!r}"
    )

    # Hard requirements should include Python
    hard_reqs_lower = [r.lower() for r in result["hard_requirements"]]
    assert any("python" in r for r in hard_reqs_lower), (
        f"Expected Python in hard_requirements, got {result['hard_requirements']!r}"
    )

    # Nice-to-haves should include kubernetes or docker
    nths_lower = [r.lower() for r in result["nice_to_haves"]]
    assert any("kubernetes" in r or "docker" in r or "graphql" in r for r in nths_lower), (
        f"Expected at least one of kubernetes/docker/graphql in nice_to_haves, "
        f"got {result['nice_to_haves']!r}"
    )

    # Boilerplate and DEI should NOT appear in requirements
    all_requirements = result["hard_requirements"] + result["nice_to_haves"]
    all_reqs_lower = [r.lower() for r in all_requirements]
    boilerplate_phrases = [
        "equal opportunity",
        "celebrate diversity",
        "inclusive environment",
        "background check",
        "authorized to work",
        "visa sponsorship",
        "health insurance",
        "401k",
        "parental leave",
    ]
    for phrase in boilerplate_phrases:
        matching = [r for r in all_reqs_lower if phrase in r]
        assert not matching, f"Boilerplate phrase {phrase!r} found in requirements: {matching!r}"

    # Culture signals should be populated
    assert len(result["culture_signals"]) > 0, (
        "Expected at least one culture signal, got empty list"
    )
