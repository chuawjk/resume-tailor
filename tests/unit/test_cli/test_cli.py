"""Unit tests for the CLI entrypoint."""

from unittest.mock import patch

from resume_tailor.cli import main

_STUB_JD_PROFILE = {
    "role_title": "Senior Software Engineer",
    "seniority": "Senior",
    "hard_requirements": ["Python"],
    "nice_to_haves": [],
    "culture_signals": [],
}

_STUB_CV_PROFILE = {
    "personal": {
        "name": "Jane Smith",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "website": "",
    },
    "education": [],
    "experience": [],
    "publications": [],
    "projects": [],
    "awards": [],
    "skills": {"technical": [], "domain": [], "soft": []},
    "other": [],
}


def _passthrough_editor(content: str, suffix: str) -> str:
    return content


def test_main_exits_zero_with_valid_paths(tmp_path, monkeypatch):
    monkeypatch.setattr("resume_tailor.cli.edit_in_editor", _passthrough_editor)
    cv_file = tmp_path / "cv.txt"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    with (
        patch("resume_tailor.workflow.extract_jd", return_value=_STUB_JD_PROFILE),
        patch("resume_tailor.workflow.extract_cv", return_value=_STUB_CV_PROFILE),
    ):
        exit_code = main(
            ["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(tmp_path)]
        )
    assert exit_code == 0


def test_main_exits_nonzero_with_missing_cv(tmp_path, capsys):
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    exit_code = main(
        [
            "--cv",
            str(tmp_path / "nonexistent.txt"),
            "--jd",
            str(jd_file),
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert exit_code != 0
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_main_exits_nonzero_with_missing_jd(tmp_path, capsys):
    cv_file = tmp_path / "cv.txt"
    cv_file.write_text("cv content")
    exit_code = main(
        [
            "--cv",
            str(cv_file),
            "--jd",
            str(tmp_path / "nonexistent.txt"),
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert exit_code != 0
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_main_creates_timestamped_run_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("resume_tailor.cli.edit_in_editor", _passthrough_editor)
    cv_file = tmp_path / "cv.txt"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    output_dir = tmp_path / "outputs"
    with (
        patch("resume_tailor.workflow.extract_jd", return_value=_STUB_JD_PROFILE),
        patch("resume_tailor.workflow.extract_cv", return_value=_STUB_CV_PROFILE),
    ):
        exit_code = main(
            ["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(output_dir)]
        )
    assert exit_code == 0
    run_dirs = list(output_dir.iterdir())
    assert len(run_dirs) == 1
    assert run_dirs[0].is_dir()


def test_main_writes_log_to_run_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("resume_tailor.cli.edit_in_editor", _passthrough_editor)
    cv_file = tmp_path / "cv.txt"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    output_dir = tmp_path / "outputs"
    with (
        patch("resume_tailor.workflow.extract_jd", return_value=_STUB_JD_PROFILE),
        patch("resume_tailor.workflow.extract_cv", return_value=_STUB_CV_PROFILE),
    ):
        main(["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(output_dir)])
    run_dir = next(output_dir.iterdir())
    assert (run_dir / "resume-tailor.log").exists()


def test_main_accepts_custom_output_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("resume_tailor.cli.edit_in_editor", _passthrough_editor)
    cv_file = tmp_path / "cv.txt"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    custom_dir = tmp_path / "my-outputs"
    with (
        patch("resume_tailor.workflow.extract_jd", return_value=_STUB_JD_PROFILE),
        patch("resume_tailor.workflow.extract_cv", return_value=_STUB_CV_PROFILE),
    ):
        exit_code = main(
            ["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(custom_dir)]
        )
    assert exit_code == 0
    assert custom_dir.exists()


def test_main_exits_nonzero_with_unsupported_cv_format(tmp_path, capsys):
    """CV files with unsupported extensions must produce an error and exit non-zero."""
    cv_file = tmp_path / "cv.odt"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    exit_code = main(["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(tmp_path)])
    assert exit_code != 0
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()
