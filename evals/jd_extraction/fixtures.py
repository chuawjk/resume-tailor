"""Eval fixtures for the JD Extraction agent.

Each fixture is a dict with:
  name        - human-readable label
  jd          - raw job description text
  checks      - grading criteria (see run_evals.py for how these are applied)
    required_in_hard      - substrings that MUST appear in hard_requirements (case-insensitive)
    forbidden_in_hard     - substrings that must NOT appear in hard_requirements
    required_in_nice      - substrings that MUST appear in nice_to_haves
    forbidden_in_nice     - substrings that must NOT appear in nice_to_haves
    seniority_options     - acceptable seniority values (case-insensitive)
    culture_signals_min   - minimum number of culture signals expected

Ship threshold: 7 of 8 fixtures must pass all their checks.
"""

FIXTURES = [
    # ------------------------------------------------------------------
    # 1. Corporate SWE posting — heavy filler, DEI, legal boilerplate
    # ------------------------------------------------------------------
    {
        "name": "Corporate SWE with boilerplate",
        "jd": """\
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

What we offer:
- Competitive salary ($150k–$200k depending on experience)
- Comprehensive health, dental, and vision insurance
- 401(k) with 4% company match

Equal Opportunity Employer
==========================
Acme Corp is an Equal Opportunity Employer. We celebrate diversity and are committed to
creating an inclusive environment for all employees. We do not discriminate on the basis of
race, religion, color, national origin, gender, or disability status.

Candidates must be authorized to work in the United States. Acme Corp does not provide
visa sponsorship for this position.
""",
        "checks": {
            "required_in_hard": ["python", "postgresql", "rest api"],
            "forbidden_in_hard": [
                "equal opportunity",
                "celebrate diversity",
                "visa sponsorship",
                "health insurance",
                "401k",
                "parental leave",
            ],
            "required_in_nice": ["kubernetes", "graphql"],
            "forbidden_in_nice": ["python", "postgresql"],
            "seniority_options": ["senior"],
            "culture_signals_min": 1,
        },
    },
    # ------------------------------------------------------------------
    # 2. Terse startup JD — minimal text, few requirements
    # ------------------------------------------------------------------
    {
        "name": "Terse startup backend engineer",
        "jd": """\
Backend Engineer — Series A fintech startup

We're a small team building payment infrastructure. Looking for a backend engineer.

Must have:
- 3+ years backend experience
- Go or Rust (we use Go)
- Comfortable with Postgres

Nice to have:
- Experience with payment systems or PCI compliance
- Prior startup experience

We're a remote team. Fast-paced. You'll own things end to end.
""",
        "checks": {
            "required_in_hard": ["go", "postgres"],
            "forbidden_in_hard": ["pci compliance", "startup experience"],
            "required_in_nice": ["payment", "startup"],
            "forbidden_in_nice": ["go", "postgres"],
            "seniority_options": ["mid-level", "senior", "junior"],
            "culture_signals_min": 1,
        },
    },
    # ------------------------------------------------------------------
    # 3. Academic posting — postdoc, different vocabulary
    # ------------------------------------------------------------------
    {
        "name": "Academic postdoc in computational biology",
        "jd": """\
Postdoctoral Research Fellow — Computational Biology
Department of Systems Biology, University of Somewhere

We invite applications for a Postdoctoral Research Fellow position in the lab of
Prof. Jane Smith. The successful candidate will develop computational methods for
single-cell RNA-seq analysis and apply them to cancer biology datasets.

Required qualifications:
- PhD in Computational Biology, Bioinformatics, Computer Science, Statistics, or a
  closely related field
- Proficiency in Python and/or R for data analysis
- Experience with single-cell sequencing data analysis (e.g. Seurat, Scanpy)
- Strong publication record commensurate with career stage
- Ability to work independently and as part of a collaborative team

Preferred qualifications:
- Experience with deep learning methods (PyTorch or TensorFlow)
- Familiarity with cancer genomics datasets (TCGA, GEO)
- Experience mentoring graduate students

The position is initially for one year, renewable contingent on performance and
funding availability. Salary is commensurate with NIH postdoctoral guidelines.

The University is an Equal Opportunity/Affirmative Action Employer.
""",
        "checks": {
            "required_in_hard": ["phd", "python"],
            "forbidden_in_hard": ["equal opportunity", "affirmative action", "salary"],
            "required_in_nice": ["deep learning", "pytorch", "tensorflow"],
            "forbidden_in_nice": ["phd", "python"],
            "seniority_options": ["entry-level", "junior", "mid-level"],
            "culture_signals_min": 0,
        },
    },
    # ------------------------------------------------------------------
    # 4. Ambiguous seniority — no explicit level stated
    # ------------------------------------------------------------------
    {
        "name": "Ambiguous seniority software engineer",
        "jd": """\
Software Engineer — Infrastructure

We're looking for a Software Engineer to join our infrastructure team. You'll build
internal tooling, improve deployment pipelines, and work closely with product teams.

What we're looking for:
- 2–4 years of experience in software engineering
- Proficiency in Python or Go
- Experience with CI/CD pipelines (GitHub Actions, CircleCI, or similar)
- Solid understanding of Linux systems

It would be great if you also have:
- Experience with Terraform or Pulumi
- AWS or GCP certifications

This is an in-office role based in London.
""",
        "checks": {
            "required_in_hard": ["python", "ci/cd", "linux"],
            "forbidden_in_hard": ["terraform", "aws certification", "gcp certification"],
            "required_in_nice": ["terraform"],
            "forbidden_in_nice": ["python", "linux"],
            "seniority_options": ["junior", "mid-level", "entry-level"],
            "culture_signals_min": 0,
        },
    },
    # ------------------------------------------------------------------
    # 5. Fintech/compliance-heavy JD
    # ------------------------------------------------------------------
    {
        "name": "Fintech engineer with compliance language",
        "jd": """\
Software Engineer II — Core Banking Platform
GlobalBank Technology Division

About GlobalBank Technology
GlobalBank is a leading financial services firm. Our technology division builds and
maintains mission-critical systems for 20 million customers worldwide.

Role overview
Join our Core Banking Platform team to build scalable, secure, and compliant financial
systems. You will work on transaction processing, ledger systems, and regulatory reporting.

Required skills:
- 3+ years experience in Java or Kotlin
- Experience building high-availability, low-latency systems
- Understanding of financial transaction processing concepts
- Familiarity with ACID database properties and distributed transactions

Preferred:
- Experience with Apache Kafka for event streaming
- Knowledge of PCI-DSS or SOX compliance requirements would be advantageous
- Prior experience in financial services or fintech

Compensation: $130,000–$160,000 plus bonus and equity
Benefits: Comprehensive medical, dental, and vision coverage; 401(k) with matching

GlobalBank is an Equal Opportunity Employer and does not discriminate on the basis of race,
color, religion, sex, national origin, age, disability, or any other protected characteristic.
Background and credit checks required for all positions.
""",
        "checks": {
            "required_in_hard": ["java", "kotlin", "high-availability"],
            "forbidden_in_hard": [
                "equal opportunity",
                "background check",
                "credit check",
                "medical",
                "dental",
                "401k",
                "compensation",
            ],
            "required_in_nice": ["kafka", "pci"],
            "forbidden_in_nice": ["java", "kotlin"],
            "seniority_options": ["mid-level", "senior"],
            "culture_signals_min": 0,
        },
    },
    # ------------------------------------------------------------------
    # 6. SRE / DevOps — infrastructure focus
    # ------------------------------------------------------------------
    {
        "name": "Site Reliability Engineer",
        "jd": """\
Site Reliability Engineer
CloudScale Inc — Remote (US)

We're looking for an SRE to join our Platform Engineering team. You'll own reliability,
observability, and incident response across our cloud-native stack.

You must have:
- 4+ years in SRE, DevOps, or Platform Engineering
- Deep experience with Kubernetes in production (cluster management, resource sizing)
- Proficiency with Terraform for infrastructure-as-code
- Experience with observability tooling: Prometheus, Grafana, OpenTelemetry
- On-call rotation participation required

Nice to have:
- Experience with service meshes (Istio, Linkerd)
- Familiarity with eBPF-based networking tools
- Contributions to open-source infrastructure projects

Our team:
- Fully remote, async-first culture
- On-call rotations are compensated
- Small team with high ownership
""",
        "checks": {
            "required_in_hard": ["kubernetes", "terraform", "prometheus"],
            "forbidden_in_hard": ["istio", "ebpf", "open-source contributions"],
            "required_in_nice": ["istio", "ebpf"],
            "forbidden_in_nice": ["kubernetes", "terraform"],
            "seniority_options": ["senior", "mid-level", "staff"],
            "culture_signals_min": 1,
        },
    },
    # ------------------------------------------------------------------
    # 7. ML / Data Science — hard vs nice-to-have classification challenge
    # ------------------------------------------------------------------
    {
        "name": "ML Engineer hard-vs-nice classification",
        "jd": """\
Machine Learning Engineer
Deepmind-adjacent AI lab (not Google) — Hybrid, San Francisco

We're building foundation models for scientific discovery. You'll work on training
pipelines, model evaluation, and productionising research prototypes.

Hard requirements:
- MSc or PhD in Machine Learning, Computer Science, or Statistics
- 3+ years professional ML engineering experience
- Strong Python skills; experience with PyTorch required
- Experience scaling distributed training (DDP, FSDP, or DeepSpeed)

We'd love it if you also have:
- Experience with RLHF or preference learning
- Familiarity with JAX or Triton
- Published research at top venues (NeurIPS, ICML, ICLR)
- Experience with LLM fine-tuning (LoRA, QLoRA)

We move fast. Small team, large compute budget. Mission-driven.
""",
        "checks": {
            "required_in_hard": ["pytorch", "python", "distributed training"],
            "forbidden_in_hard": ["rlhf", "jax", "triton", "lora", "published research"],
            "required_in_nice": ["rlhf", "jax"],
            "forbidden_in_nice": ["pytorch", "python"],
            "seniority_options": ["senior", "mid-level", "staff"],
            "culture_signals_min": 1,
        },
    },
    # ------------------------------------------------------------------
    # 8. Product Manager — non-engineering, tests breadth of schema
    # ------------------------------------------------------------------
    {
        "name": "Product Manager non-engineering role",
        "jd": """\
Senior Product Manager — Developer Tools
BuildFast Inc

We're looking for a Senior PM to own our developer tools product line, working
closely with engineering, design, and enterprise customers.

Required:
- 5+ years in product management, with at least 2 years focused on developer or
  technical products
- Demonstrated ability to write detailed product specs and translate them to
  engineering requirements
- Experience running customer discovery interviews with developers
- Comfort with quantitative analysis: defining metrics, reading dashboards,
  interpreting A/B tests

Preferred:
- Prior software engineering experience (any language)
- Experience with PLG (product-led growth) strategies
- Familiarity with Jira, Figma, and Amplitude

Culture:
- High autonomy — PMs here own roadmap and prioritisation
- Strong writing culture, async by default
- Direct access to customers encouraged

Salary range: $160k–$200k. We do not sponsor visas.
""",
        "checks": {
            "required_in_hard": ["product management", "customer discovery"],
            "forbidden_in_hard": [
                "visa",
                "salary",
                "jira",
                "figma",
                "amplitude",
                "prior software engineering",
            ],
            "required_in_nice": ["engineering experience", "plg"],
            "forbidden_in_nice": ["product management", "customer discovery"],
            "seniority_options": ["senior"],
            "culture_signals_min": 1,
        },
    },
]
