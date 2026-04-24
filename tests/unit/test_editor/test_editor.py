"""Unit tests for resume_tailor.editor.edit_in_editor."""

import os

import pytest

from resume_tailor.editor import edit_in_editor


def _make_writing_editor(new_content: str):
    def fake_run(cmd, **kwargs):
        path = cmd[-1]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return fake_run


def _noop_editor(cmd, **kwargs):
    pass


def test_happy_path_returns_edited_content(monkeypatch):
    monkeypatch.setenv("EDITOR", "fake-editor")
    monkeypatch.setattr("subprocess.run", _make_writing_editor("edited content"))
    result = edit_in_editor("original content", ".json")
    assert result == "edited content"


def test_no_edit_returns_original_content(monkeypatch):
    monkeypatch.setenv("EDITOR", "fake-editor")
    monkeypatch.setattr("subprocess.run", _noop_editor)
    original = "unchanged content"
    result = edit_in_editor(original, ".md")
    assert result == original


def test_falls_back_to_vi_when_editor_not_set(monkeypatch):
    monkeypatch.delenv("EDITOR", raising=False)
    captured_cmd = []

    def capture_run(cmd, **kwargs):
        captured_cmd.extend(cmd)

    monkeypatch.setattr("subprocess.run", capture_run)
    edit_in_editor("content", ".txt")
    assert captured_cmd[0] == "vi"


def test_temp_file_cleaned_up_after_edit(monkeypatch):
    monkeypatch.setenv("EDITOR", "fake-editor")
    captured_path = []

    def capture_path_and_noop(cmd, **kwargs):
        captured_path.append(cmd[-1])

    monkeypatch.setattr("subprocess.run", capture_path_and_noop)
    edit_in_editor("content", ".json")
    assert not os.path.exists(captured_path[0])


def test_temp_file_cleaned_up_on_exception(monkeypatch):
    monkeypatch.setenv("EDITOR", "nonexistent-binary-xyz")
    captured_path = []

    def raise_file_not_found(cmd, **kwargs):
        captured_path.append(cmd[-1])
        raise FileNotFoundError(f"No such file or directory: '{cmd[0]}'")

    monkeypatch.setattr("subprocess.run", raise_file_not_found)
    with pytest.raises(FileNotFoundError):
        edit_in_editor("content", ".json")
    assert not os.path.exists(captured_path[0])


def test_editor_not_found_raises_file_not_found_error(monkeypatch):
    monkeypatch.setenv("EDITOR", "nonexistent-binary-xyz")

    def raise_file_not_found(cmd, **kwargs):
        raise FileNotFoundError(f"No such file or directory: '{cmd[0]}'")

    monkeypatch.setattr("subprocess.run", raise_file_not_found)
    with pytest.raises(FileNotFoundError):
        edit_in_editor("content", ".json")


def test_suffix_appears_in_temp_file_name(monkeypatch):
    monkeypatch.setenv("EDITOR", "fake-editor")
    captured_path = []

    def capture_path_and_noop(cmd, **kwargs):
        captured_path.append(cmd[-1])

    monkeypatch.setattr("subprocess.run", capture_path_and_noop)
    edit_in_editor("content", ".json")
    assert captured_path[0].endswith(".json")


def test_unicode_content_round_trips_correctly(monkeypatch):
    monkeypatch.setenv("EDITOR", "fake-editor")
    monkeypatch.setattr("subprocess.run", _noop_editor)
    unicode_content = "résumé: café, naïve, Ångström"
    result = edit_in_editor(unicode_content, ".md")
    assert result == unicode_content
