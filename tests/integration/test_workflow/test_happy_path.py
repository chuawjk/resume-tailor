"""Integration test: full workflow with passthrough editor."""

from unittest.mock import patch

from resume_tailor.cli import main

_STUB_CV_PROFILE = {
    "personal": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "",
        "location": "",
        "linkedin": "",
        "website": "",
    },
    "education": [],
    "experience": [
        {
            "role": "Software Engineer",
            "organisation": "Acme Corp",
            "start_date": "2015",
            "end_date": "2023",
            "responsibilities": ["Built REST APIs"],
            "achievements": [],
            "skills_demonstrated": ["Python"],
        }
    ],
    "publications": [],
    "projects": [],
    "awards": [],
    "skills": {"technical": ["Python", "PostgreSQL"], "domain": [], "soft": []},
    "other": [],
}


def passthrough_editor(content: str, suffix: str) -> str:
    return content


def test_happy_path_produces_resume_md(tmp_path, monkeypatch):
    monkeypatch.setattr("resume_tailor.cli.edit_in_editor", passthrough_editor)

    cv_file = tmp_path / "cv.txt"
    cv_file.write_text("CV content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("Job description content")
    output_dir = tmp_path / "outputs"
    output_file = tmp_path / "resume.md"

    with patch("resume_tailor.workflow.extract_cv", return_value=_STUB_CV_PROFILE):
        exit_code = main(
            [
                "--cv",
                str(cv_file),
                "--jd",
                str(jd_file),
                "--output-dir",
                str(output_dir),
                "--output",
                str(output_file),
            ]
        )

    assert exit_code == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert len(content) > 0
    assert "Jane Smith" in content  # stub resume content
    assert "<!-- FABRICATION_REPORT" not in content  # sentinel stripped before saving
    assert content.startswith("#")  # valid markdown heading
