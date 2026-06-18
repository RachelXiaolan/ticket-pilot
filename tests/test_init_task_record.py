"""Smoke tests for scripts/init_task_record.py input validation.

Run: python3 -m pytest tests/   OR   python3 tests/test_init_task_record.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Load module without executing main()
spec = importlib.util.spec_from_file_location(
    "init_task_record", SCRIPTS_DIR / "init_task_record.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ValidateIssueIdTests(unittest.TestCase):
    def test_accepts_valid_id(self):
        self.assertEqual(mod._validate_issue_id("AI-2134"), "AI-2134")

    def test_accepts_team_key_with_digits(self):
        self.assertEqual(mod._validate_issue_id("ENG2-9"), "ENG2-9")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id("")

    def test_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id("../etc/passwd")

    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id("/etc/passwd")

    def test_rejects_newline(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id("AI-2134\nrm -rf /")

    def test_lowercase_normalized(self):
        # Linear team keys are uppercase by convention but the validator is
        # lenient and normalizes to upper case so the dir name is canonical.
        self.assertEqual(mod._validate_issue_id("ai-2134"), "AI-2134")

    def test_rejects_whitespace(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id(" AI-2134 ")
        with self.assertRaises(ValueError):
            mod._validate_issue_id("AI-2134\t")

    def test_rejects_no_dash(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id("AI2134")

    def test_rejects_no_number(self):
        with self.assertRaises(ValueError):
            mod._validate_issue_id("AI-")


class ValidateRootTests(unittest.TestCase):
    def test_accepts_relative(self):
        self.assertEqual(mod._validate_root("tasks"), Path("tasks"))

    def test_rejects_absolute(self):
        with self.assertRaises(ValueError):
            mod._validate_root("/tmp/foo")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            mod._validate_root("")

    def test_rejects_traversal(self):
        with self.assertRaises(ValueError):
            mod._validate_root("../escape")

    def test_rejects_hidden_traversal(self):
        with self.assertRaises(ValueError):
            mod._validate_root("tasks/../escape")


class EndToEndTests(unittest.TestCase):
    """Exercise the script's main() via a subprocess to confirm argv parsing
    also rejects bad inputs."""

    def run_script(self, *args, env=None):
        import subprocess
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "init_task_record.py"), *args],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
            env=env,
        )

    def test_happy_path(self):
        r = self.run_script("AI-2134", "--title", "demo", "--root", "tmp_tasks_e2e")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(Path("tmp_tasks_e2e/AI-2134/task.json").exists())
        # cleanup
        import shutil
        shutil.rmtree("tmp_tasks_e2e", ignore_errors=True)

    def test_rejects_traversal_via_argv(self):
        r = self.run_script("../escape", "--root", "tmp_tasks_e2e2")
        self.assertEqual(r.returncode, 2)
        self.assertTrue(
            "not a valid Linear identifier" in r.stderr
            or "disallowed characters" in r.stderr,
            r.stderr,
        )

    def test_rejects_empty_via_argv(self):
        r = self.run_script("", "--root", "tmp_tasks_e2e3")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
