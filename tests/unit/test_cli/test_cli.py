"""Unit tests for the CLI entrypoint."""

import tempfile

from resume_tailor.cli import main


def test_main_exits_zero_with_valid_paths(tmp_path, capsys):
    with (
        tempfile.NamedTemporaryFile(suffix=".pdf") as cv_file,
        tempfile.NamedTemporaryFile(suffix=".txt") as jd_file,
    ):
        exit_code = main(
            ["--cv", cv_file.name, "--jd", jd_file.name, "--output-dir", str(tmp_path)]
        )
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "not implemented" in captured.out.lower()


def test_main_exits_nonzero_with_missing_cv(tmp_path, capsys):
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    exit_code = main(
        [
            "--cv",
            str(tmp_path / "nonexistent.pdf"),
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
    cv_file = tmp_path / "cv.pdf"
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


def test_main_creates_timestamped_run_dir(tmp_path):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    output_dir = tmp_path / "outputs"
    exit_code = main(["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(output_dir)])
    assert exit_code == 0
    run_dirs = list(output_dir.iterdir())
    assert len(run_dirs) == 1
    assert run_dirs[0].is_dir()


def test_main_writes_log_to_run_dir(tmp_path):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    output_dir = tmp_path / "outputs"
    main(["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(output_dir)])
    run_dir = next(output_dir.iterdir())
    assert (run_dir / "resume-tailor.log").exists()


def test_main_accepts_custom_output_dir(tmp_path):
    cv_file = tmp_path / "cv.pdf"
    cv_file.write_text("cv content")
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("job description")
    custom_dir = tmp_path / "my-outputs"
    exit_code = main(["--cv", str(cv_file), "--jd", str(jd_file), "--output-dir", str(custom_dir)])
    assert exit_code == 0
    assert custom_dir.exists()
