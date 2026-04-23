"""Unit tests for the CLI entrypoint."""

import tempfile

from resume_tailor.cli import main


def test_main_exits_zero_with_valid_paths(capsys):
    with (
        tempfile.NamedTemporaryFile(suffix=".pdf") as cv_file,
        tempfile.NamedTemporaryFile(suffix=".txt") as jd_file,
    ):
        exit_code = main(["--cv", cv_file.name, "--jd", jd_file.name])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "not implemented" in captured.out.lower()


def test_main_exits_nonzero_with_missing_cv(tmp_path, capsys):
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    exit_code = main(["--cv", str(tmp_path / "nonexistent.pdf"), "--jd", str(jd_file)])
    assert exit_code != 0
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_main_exits_nonzero_with_missing_jd(tmp_path, capsys):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("cv content")
    exit_code = main(["--cv", str(cv_file), "--jd", str(tmp_path / "nonexistent.txt")])
    assert exit_code != 0
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_main_output_default_is_resume_md(tmp_path, capsys):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    exit_code = main(["--cv", str(cv_file), "--jd", str(jd_file)])
    assert exit_code == 0


def test_main_accepts_custom_output(tmp_path, capsys):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    exit_code = main(["--cv", str(cv_file), "--jd", str(jd_file), "--output", "custom.md"])
    assert exit_code == 0
