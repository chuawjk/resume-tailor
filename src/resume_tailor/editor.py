"""Editor helper — opens content in the user's $EDITOR and returns edited result."""

import os
import subprocess
import tempfile


def edit_in_editor(content: str, suffix: str) -> str:
    editor_cmd = os.environ.get("EDITOR", "vi").split()
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name
    try:
        subprocess.run([*editor_cmd, path], check=False)
        with open(path, encoding="utf-8") as f:
            return f.read()
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
