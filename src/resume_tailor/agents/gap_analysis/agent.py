"""Gap Analysis Agent — stub implementation."""


def analyse_gaps(jd_profile: dict, cv_profile: dict) -> dict:
    return {
        "strong_matches": ["Python", "REST APIs", "PostgreSQL"],
        "weak_matches": [
            {
                "requirement": "Kubernetes",
                "evidence": "No direct mention in CV",
                "user_note": None,
            }
        ],
        "gaps": [{"requirement": "GraphQL", "acknowledged": True}],
    }
