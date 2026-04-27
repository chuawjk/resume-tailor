"""Eval fixtures for the CV Extraction agent.

Each fixture is a dict with:
  name        - human-readable label
  cv          - raw CV text
  checks      - grading criteria (see run_evals.py for how these are applied)
    required_name               - exact name string that must appear in personal.name
    required_in_experience_roles - list of substrings that must appear in at least one
                                   experience entry's role
    required_technical_skills   - list of substrings that must appear in skills.technical
    min_experience_count        - minimum number of experience entries expected

Ship threshold: 3 of 4 fixtures must pass all their checks.
"""

FIXTURES = [
    # ------------------------------------------------------------------
    # 1. Software engineer with full sections (education, experience,
    #    skills, certifications as other)
    # ------------------------------------------------------------------
    {
        "name": "Software engineer with full sections",
        "cv": """\
Alex Johnson
alex.johnson@email.com | +1-415-555-0101 | San Francisco, CA
linkedin.com/in/alexjohnson | alexjohnson.dev

EDUCATION
---------
BSc Computer Science, Stanford University, 2018
GPA: 3.7/4.0

EXPERIENCE
----------
Senior Software Engineer, Stripe, Jan 2021 – Present
- Designed and maintained payment processing microservices handling 10M+ transactions/day
- Led migration from monolith to event-driven architecture using Kafka
- Mentored 3 junior engineers

Software Engineer, Dropbox, Jun 2018 – Dec 2020
- Built file synchronisation backend in Python and Go
- Reduced sync latency by 40% through protocol optimisations
- Wrote integration tests achieving 95% coverage

SKILLS
------
Technical: Python, Go, Kafka, PostgreSQL, Kubernetes, Docker, AWS, gRPC
Domain: Distributed systems, Payment processing, Backend engineering
Soft: Mentoring, Technical writing, Problem-solving

CERTIFICATIONS
--------------
AWS Certified Solutions Architect – Professional (2022)
Certified Kubernetes Administrator (CKA) (2023)
""",
        "checks": {
            "required_name": "Alex Johnson",
            "required_in_experience_roles": ["Senior Software Engineer", "Software Engineer"],
            "required_technical_skills": ["Python", "Go", "Kafka"],
            "min_experience_count": 2,
        },
    },
    # ------------------------------------------------------------------
    # 2. Academic researcher with publications
    # ------------------------------------------------------------------
    {
        "name": "Academic researcher with publications",
        "cv": """\
Dr. Sarah Chen
sarah.chen@university.edu | +44-20-7946-0101 | London, UK
scholar.google.com/citations?user=sarahchen

EDUCATION
---------
PhD in Computational Neuroscience, University College London, 2019
Thesis: "Deep learning models for spike sorting in large-scale neural recordings"

MSc Neuroscience, Imperial College London, 2014

BSc Biological Sciences, University of Edinburgh, 2013

RESEARCH EXPERIENCE
-------------------
Postdoctoral Research Fellow, UCL Gatsby Computational Neuroscience Unit, Sep 2019 – Present
- Developed Bayesian methods for neural data analysis
- Supervised 2 PhD students and 4 MSc students

Research Assistant, MRC Brain Network Dynamics Unit, Oct 2014 – Aug 2015
- Assisted with electrophysiology data collection and analysis using MATLAB

PUBLICATIONS
------------
Chen, S., Williams, T., & Bhatt, D. (2022). "Scalable spike sorting with deep neural networks."
  Nature Methods, 19(4), 412–421.

Chen, S., & Bhatt, D. (2021). "Variational inference for latent neural dynamics."
  NeurIPS 2021 Proceedings.

Chen, S. (2020). "A tutorial on Gaussian process regression for neuroscientists."
  Journal of Neuroscience Methods, 340, 108715.

SKILLS
------
Technical: Python, MATLAB, PyTorch, NumPy, Stan, R, Julia
Domain: Computational neuroscience, Bayesian inference, Deep learning
Soft: Scientific writing, Supervision, Collaboration

AWARDS
------
Wellcome Trust Early Career Research Award, 2021
Best Poster Award, Cosyne 2020
""",
        "checks": {
            "required_name": "Dr. Sarah Chen",
            "required_in_experience_roles": ["Postdoctoral Research Fellow"],
            "required_technical_skills": ["Python", "PyTorch"],
            "min_experience_count": 1,
        },
    },
    # ------------------------------------------------------------------
    # 3. Career changer with a short CV
    # ------------------------------------------------------------------
    {
        "name": "Career changer with short CV",
        "cv": """\
Maria Gonzalez
maria.g@gmail.com | +1-312-555-0202 | Chicago, IL

OBJECTIVE
---------
Transitioning from marketing to data analytics. Completed intensive data science bootcamp
and looking for entry-level analyst role.

EDUCATION
---------
Data Science Bootcamp, General Assembly, 2023

BA Marketing, DePaul University, 2017

EXPERIENCE
----------
Marketing Analyst, RetailCo, Aug 2017 – Mar 2023
- Managed $500k annual digital advertising budget across Google Ads and Facebook
- Produced monthly performance reports using Excel and Google Sheets
- Collaborated with data team to implement UTM tracking

PROJECTS
--------
Sales Forecasting Dashboard
- Built interactive Tableau dashboard predicting monthly sales using regression models
- Deployed using Python (pandas, scikit-learn) and connected to PostgreSQL database

SKILLS
------
Technical: Python, SQL, Tableau, Excel, pandas, scikit-learn
Domain: Marketing analytics, Data visualisation, A/B testing
Soft: Communication, Stakeholder management
""",
        "checks": {
            "required_name": "Maria Gonzalez",
            "required_in_experience_roles": ["Marketing Analyst"],
            "required_technical_skills": ["Python", "SQL"],
            "min_experience_count": 1,
        },
    },
    # ------------------------------------------------------------------
    # 4. Senior engineer with many experience entries
    # ------------------------------------------------------------------
    {
        "name": "Senior engineer with many experience entries",
        "cv": """\
James Okafor
james.okafor@protonmail.com | +1-206-555-0303 | Seattle, WA
linkedin.com/in/jamesokafor | github.com/jokafor

SUMMARY
-------
Principal engineer with 15 years of experience building large-scale distributed systems.
Specialist in real-time data pipelines and cloud infrastructure.

EDUCATION
---------
MEng Computer Engineering, Georgia Institute of Technology, 2009

BSc Electrical Engineering, University of Lagos, 2007

EXPERIENCE
----------
Principal Engineer, Amazon Web Services, Mar 2020 – Present
- Technical lead for S3 durability team, 11 direct reports
- Drove architecture for cross-region replication achieving 99.999999999% durability
- Reduced operational costs by $12M annually through storage tiering improvements

Staff Engineer, Confluent, Jan 2017 – Feb 2020
- Led development of Kafka Connect framework extensions for 50+ connectors
- Partnered with Confluent Cloud team to migrate on-prem enterprise clients

Senior Software Engineer, Palantir Technologies, Aug 2014 – Dec 2016
- Built data ingestion pipelines processing 5TB/day for government clients
- Developed custom security classification layer for multi-tenant deployments

Software Engineer, Microsoft, Jun 2011 – Jul 2014
- Worked on Azure Storage distributed file system team
- Contributed to public preview launch of Azure Blob Storage

Software Engineer, Cisco Systems, Jul 2009 – May 2011
- Implemented network protocol monitoring tools in C++ and Java

SKILLS
------
Technical: Java, Python, C++, Scala, Kafka, Spark, Kubernetes, Terraform, AWS, GCP
Domain: Distributed systems, Real-time data pipelines, Cloud infrastructure, Storage systems
Soft: Technical leadership, Mentoring, Cross-functional collaboration

AWARDS
------
Amazon Bar Raiser (2022)
Confluent Engineering Excellence Award (2019)

PUBLICATIONS
------------
Okafor, J., & Smith, R. (2018). "Fault-tolerant exactly-once semantics in Kafka."
  IEEE Transactions on Parallel and Distributed Systems.
""",
        "checks": {
            "required_name": "James Okafor",
            "required_in_experience_roles": ["Principal Engineer", "Staff Engineer"],
            "required_technical_skills": ["Java", "Python", "Kafka"],
            "min_experience_count": 4,
        },
    },
]
