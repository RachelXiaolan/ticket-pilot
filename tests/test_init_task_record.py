"""Tests for init_task_record.py — guards against stale notes & silent permission errors."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "init_task_record.py"


def run(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=cwd,
    )


def test_first_run_creates_both_files():
    with tempfile.TemporaryDirectory() as tmp:
        r = run(["AI-1111", "--title", "hello", "--repo", "x/y", "--branch", "b", "--root", f"{tmp}/tasks"])
        assert r.returncode == 0, r.stderr
        tj = Path(tmp) / "tasks" / "AI-1111" / "task.json"
        nm = Path(tmp) / "tasks" / "AI-1111" / "notes.md"
        assert tj.exists()
        assert nm.exists()
        body = json.loads(tj.read_text())
        assert body["title"] == "hello"
        assert body["repo"] == "x/y"
        assert body["branch"] == "b"


def test_repeat_run_refuses_without_force():
    """Regression: the old code rewrote task.json but kept a stale notes.md from a previous issue.
    New code must refuse to partially overwrite unless --force is given."""
    with tempfile.TemporaryDirectory() as tmp:
        # First run
        r1 = run(["AI-2222", "--title", "first", "--repo", "x/y", "--branch", "b1", "--root", f"{tmp}/tasks"])
        assert r1.returncode == 0, r1.stderr

        # Mutate notes.md to look like previous-task content
        notes = Path(tmp) / "tasks" / "AI-2222" / "notes.md"
        notes.write_text("# AI-2222 Notes\n\n## Scope\n- original scope\n")

        # Second run with NEW title/branch — must NOT silently partial-overwrite
        r2 = run(["AI-2222", "--title", "DIFFERENT", "--repo", "z/w", "--branch", "b2", "--root", f"{tmp}/tasks"])
        assert r2.returncode != 0, f"expected refusal, got rc=0 stdout={r2.stdout!r} stderr={r2.stderr!r}"
        assert "already exists" in r2.stderr

        # Old notes.md content preserved (no partial overwrite happened)
        assert "original scope" in notes.read_text()

        # task.json preserved too
        tj = json.loads((Path(tmp) / "tasks" / "AI-2222" / "task.json").read_text())
        assert tj["title"] == "first"


def test_force_overwrites_atomically():
    with tempfile.TemporaryDirectory() as tmp:
        run(["AI-3333", "--title", "old", "--root", f"{tmp}/tasks"])
        r = run(["AI-3333", "--title", "new", "--root", f"{tmp}/tasks", "--force"])
        assert r.returncode == 0, r.stderr
        tj = json.loads((Path(tmp) / "tasks" / "AI-3333" / "task.json").read_text())
        assert tj["title"] == "new"
        notes = (Path(tmp) / "tasks" / "AI-3333" / "notes.md").read_text()
        assert "Started task artifact" in notes  # notes got refreshed


def test_permission_error_exits_cleanly():
    """Old code crashed with a PermissionError traceback. New code must exit non-zero with a clear message."""
    with tempfile.TemporaryDirectory() as tmp:
        ro = Path(tmp) / "ro"
        ro.mkdir()
        os.chmod(ro, 0o555)
        try:
            r = run(["AI-4444", "--title", "x", "--root", f"{ro}/tasks"])
            assert r.returncode != 0, f"expected non-zero, got {r.returncode}"
            assert "permission denied" in r.stderr.lower() or "Permission denied" in r.stderr
            # No partial folder was left behind
            assert not (ro / "AI-4444").exists()
        finally:
            os.chmod(ro, 0o755)


if __name__ == "__main__":
    import traceback
    tests = [
        test_first_run_creates_both_files,
        test_repeat_run_refuses_without_force,
        test_force_overwrites_atomically,
        test_permission_error_exits_cleanly,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
