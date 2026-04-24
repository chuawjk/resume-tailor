"""CV Extraction Agent — stub implementation."""


def extract_cv(cv_text: str) -> dict:
    return {
        "personal": {"name": "Jane Smith", "email": "jane@example.com"},
        "education": [
            {
                "degree": "BSc Computer Science",
                "institution": "University of Example",
                "year": "2015",
            }
        ],
        "experience": [
            {
                "role": "Software Engineer",
                "organisation": "Acme Corp",
                "duration": "2015–2023",
                "responsibilities": ["Built REST APIs", "Maintained PostgreSQL databases"],
                "achievements": ["Reduced latency by 30%"],
                "skills_demonstrated": ["Python", "PostgreSQL"],
            }
        ],
        "publications": [],
        "projects": [],
        "awards": [],
        "skills": {
            "technical": ["Python", "PostgreSQL", "REST APIs"],
            "domain": ["Backend engineering"],
            "soft": ["communication", "problem-solving"],
        },
        "other": [],
    }
