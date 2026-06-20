from __future__ import annotations

import importlib.util
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sync_comment.py"
SPEC = importlib.util.spec_from_file_location("sync_comment", SCRIPT_PATH)
sync_comment = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sync_comment)


def completed(stdout: str, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["curl"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class LinearCommentTests(unittest.TestCase):
    def test_linear_comment_returns_id_on_success(self):
        payload = '{"data":{"commentCreate":{"comment":{"id":"comment-123456"}}}}'

        with (
            mock.patch.dict(os.environ, {"LINEAR_API_KEY": "lin_test"}),
            mock.patch.object(sync_comment.subprocess, "run", return_value=completed(payload)),
        ):
            self.assertEqual(sync_comment.linear_comment("AI-1", "body"), "comment-123456")

    def test_linear_comment_returns_none_on_curl_failure(self):
        with (
            mock.patch.dict(os.environ, {"LINEAR_API_KEY": "lin_test"}),
            mock.patch.object(
                sync_comment.subprocess,
                "run",
                return_value=completed("", returncode=6, stderr="Could not resolve host"),
            ),
        ):
            self.assertIsNone(sync_comment.linear_comment("AI-1", "body"))

    def test_linear_comment_returns_none_on_invalid_json(self):
        with (
            mock.patch.dict(os.environ, {"LINEAR_API_KEY": "lin_test"}),
            mock.patch.object(sync_comment.subprocess, "run", return_value=completed("not json")),
        ):
            self.assertIsNone(sync_comment.linear_comment("AI-1", "body"))


if __name__ == "__main__":
    unittest.main()
