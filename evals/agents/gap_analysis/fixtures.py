"""Eval fixtures for the Gap Analysis agent.

Each fixture is a dict with:
  name              - human-readable label
  jd_profile        - structured JD profile dict (from extract_jd)
  cv_profile        - structured CV profile dict (from extract_cv)
  checks            - grading criteria (see run_evals.py for how these are applied)
    expected_in_strong  - substrings that MUST appear in at least one strong_matches string
    expected_in_gaps    - substrings that MUST appear in at least one gaps[i]["requirement"]
    total_requirements  - len(hard_requirements) + len(nice_to_haves); used to check no drops

Ship threshold: 4 of 5 fixtures must pass all their checks.
"""

FIXTURES = [
    # ------------------------------------------------------------------
    # 1. Direct match — exact vocabulary, no semantic inference needed
    # ------------------------------------------------------------------
    {
        "name": "Direct match — backend engineer",
        "jd_profile": {
            "role_title": "Backend Engineer",
            "seniority": "Senior",
            "hard_requirements": [
                "Python",
                "PostgreSQL",
                "REST API design",
                "Docker",
            ],
            "nice_to_haves": ["Kubernetes", "GraphQL"],
            "culture_signals": ["fast-paced"],
        },
        "cv_profile": {
            "personal": {"name": "Jane Smith", "email": "jane@example.com"},
            "skills": {
                "technical": ["Python", "PostgreSQL", "Docker", "Kubernetes"],
                "domain": ["Backend Engineering"],
                "soft": [],
            },
            "experience": [
                {
                    "role": "Senior Software Engineer",
                    "organisation": "Acme Corp",
                    "start_date": "2019",
                    "end_date": "Present",
                    "responsibilities": [
                        "Designed and built REST APIs serving 10M requests/day",
                        "Managed Docker containers in production",
                    ],
                    "achievements": ["Reduced API latency by 40%"],
                    "skills_demonstrated": ["Python", "PostgreSQL", "REST API", "Docker"],
                }
            ],
            "education": [],
            "publications": [],
            "projects": [],
            "awards": [],
            "other": [],
        },
        "checks": {
            "expected_in_strong": ["python", "postgresql", "rest api", "docker", "kubernetes"],
            "expected_in_gaps": ["graphql"],
            "total_requirements": 6,
        },
    },
    # ------------------------------------------------------------------
    # 2. Vocabulary mismatch — semantic matching required
    # ------------------------------------------------------------------
    {
        "name": "Vocabulary mismatch — k8s / ML / Postgres",
        "jd_profile": {
            "role_title": "ML Platform Engineer",
            "seniority": "Senior",
            "hard_requirements": [
                "Kubernetes (k8s)",
                "machine learning pipeline experience",
                "Postgres",
            ],
            "nice_to_haves": ["RLHF fine-tuning", "Triton"],
            "culture_signals": [],
        },
        "cv_profile": {
            "personal": {"name": "Alex Chen", "email": "alex@example.com"},
            "skills": {
                "technical": ["Kubernetes", "PostgreSQL", "Python", "PyTorch"],
                "domain": ["Machine Learning", "Platform Engineering"],
                "soft": [],
            },
            "experience": [
                {
                    "role": "ML Engineer",
                    "organisation": "DataCo",
                    "start_date": "2020",
                    "end_date": "Present",
                    "responsibilities": [
                        "Built ML training pipelines with PyTorch and Kubeflow",
                        "Orchestrated workloads on Kubernetes clusters",
                    ],
                    "achievements": [],
                    "skills_demonstrated": ["Kubernetes", "PyTorch", "PostgreSQL"],
                }
            ],
            "education": [],
            "publications": [],
            "projects": [],
            "awards": [],
            "other": [],
        },
        "checks": {
            "expected_in_strong": ["kubernetes", "machine learning", "postgres"],
            "expected_in_gaps": ["rlhf", "triton"],
            "total_requirements": 5,
        },
    },
    # ------------------------------------------------------------------
    # 3. Partial / weak matches — genuine evidence exists but not direct
    # ------------------------------------------------------------------
    {
        "name": "Weak matches with genuine CV evidence",
        "jd_profile": {
            "role_title": "Engineering Manager",
            "seniority": "Senior",
            "hard_requirements": [
                "team lead / people management",
                "5+ years Python",
                "CI/CD pipeline ownership",
                "AWS production experience",
            ],
            "nice_to_haves": ["Terraform", "Go"],
            "culture_signals": [],
        },
        "cv_profile": {
            "personal": {"name": "Sam Rivera", "email": "sam@example.com"},
            "skills": {
                "technical": ["Python", "GitHub Actions", "AWS S3", "CloudFront"],
                "domain": ["Backend Engineering"],
                "soft": ["mentoring", "communication"],
            },
            "experience": [
                {
                    "role": "Senior Software Engineer",
                    "organisation": "StartupXYZ",
                    "start_date": "2016",
                    "end_date": "Present",
                    "responsibilities": [
                        "Mentored 3 junior engineers and ran weekly 1-on-1s",
                        "Configured GitHub Actions CI/CD pipelines for 5 services",
                        "Used AWS S3 and CloudFront for static asset delivery",
                        "7 years of Python development across multiple projects",
                    ],
                    "achievements": [],
                    "skills_demonstrated": ["Python", "GitHub Actions", "AWS"],
                }
            ],
            "education": [],
            "publications": [],
            "projects": [],
            "awards": [],
            "other": [],
        },
        "checks": {
            "expected_in_strong": ["python"],
            "expected_in_gaps": ["terraform", "go"],
            "total_requirements": 6,
        },
    },
    # ------------------------------------------------------------------
    # 4. Domain mismatch — related but not equivalent technology
    # ------------------------------------------------------------------
    {
        "name": "Domain mismatch — Kafka vs Flink",
        "jd_profile": {
            "role_title": "Streaming Data Engineer",
            "seniority": "Senior",
            "hard_requirements": [
                "Apache Flink or Spark Streaming",
                "Kafka consumer group management",
                "JVM performance tuning",
            ],
            "nice_to_haves": ["Flink SQL", "ksqlDB"],
            "culture_signals": [],
        },
        "cv_profile": {
            "personal": {"name": "Jordan Lee", "email": "jordan@example.com"},
            "skills": {
                "technical": ["Kafka", "Java", "Python", "Spark"],
                "domain": ["Data Engineering", "Streaming"],
                "soft": [],
            },
            "experience": [
                {
                    "role": "Data Engineer",
                    "organisation": "StreamCo",
                    "start_date": "2018",
                    "end_date": "Present",
                    "responsibilities": [
                        "Built real-time data pipelines using Kafka and Spark",
                        "Managed Kafka topics and consumer groups",
                    ],
                    "achievements": [],
                    "skills_demonstrated": ["Kafka", "Spark", "Java"],
                }
            ],
            "education": [],
            "publications": [],
            "projects": [],
            "awards": [],
            "other": [],
        },
        "checks": {
            "expected_in_strong": [],
            "expected_in_gaps": ["flink sql", "ksqldb", "jvm"],
            "total_requirements": 5,
        },
    },
    # ------------------------------------------------------------------
    # 5. Academic CV vs commercial SWE JD — clear gaps, one open-source weak match
    # ------------------------------------------------------------------
    {
        "name": "Academic CV vs commercial SWE JD",
        "jd_profile": {
            "role_title": "Software Engineer",
            "seniority": "Mid-level",
            "hard_requirements": [
                "production deployment experience",
                "5+ years commercial software engineering",
                "incident response / on-call",
            ],
            "nice_to_haves": ["startup experience", "open-source contributions"],
            "culture_signals": [],
        },
        "cv_profile": {
            "personal": {"name": "Dr. Priya Nair", "email": "priya@university.edu"},
            "skills": {
                "technical": ["Python", "MATLAB", "R", "NumPy", "Pandas"],
                "domain": ["Computational Biology", "Data Analysis"],
                "soft": ["research", "writing"],
            },
            "experience": [
                {
                    "role": "Postdoctoral Researcher",
                    "organisation": "University of Somewhere",
                    "start_date": "2021",
                    "end_date": "Present",
                    "responsibilities": [
                        "Developed computational methods for single-cell RNA-seq analysis",
                        "Published 3 papers in Nature Methods and Bioinformatics",
                    ],
                    "achievements": [],
                    "skills_demonstrated": ["Python", "R", "MATLAB"],
                }
            ],
            "education": [
                {
                    "degree": "PhD Computational Biology",
                    "institution": "MIT",
                    "year": "2021",
                    "gpa": "",
                }
            ],
            "publications": [
                {
                    "title": "scRNA-seq analysis methods",
                    "venue": "Nature Methods",
                    "year": "2023",
                    "authors": ["Priya Nair"],
                }
            ],
            "projects": [
                {
                    "name": "sctools",
                    "description": "Open-source Python library for single-cell analysis",
                    "technologies": ["Python"],
                    "url": "https://github.com/priya/sctools",
                }
            ],
            "awards": [],
            "other": [],
        },
        "checks": {
            "expected_in_strong": [],
            "expected_in_gaps": [
                "production deployment",
                "commercial software",
                "incident response",
                "startup",
            ],
            "total_requirements": 5,
        },
    },
]
