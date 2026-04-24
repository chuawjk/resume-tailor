"""Integration test: full workflow with passthrough editor."""

from resume_tailor.cli import main


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
