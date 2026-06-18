"""Test that linear_comment returns None on GraphQL errors and never raises."""
import sys, json, subprocess
from unittest import mock

sys.path.insert(0, "/home/codespace/work/ticket-pilot/scripts")
import sync_comment
import os


def test_returns_none_when_stdout_empty():
    """curl may return empty stdout on network failure. Must not raise JSONDecodeError."""
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="curl: (6) Could not resolve")
    with mock.patch.object(subprocess, "run", return_value=fake):
        with mock.patch.dict(os.environ, {"LINEAR_API_KEY": "fake-key"}):
            result = sync_comment.linear_comment("AI-2137", "test body")
    assert result is None, f"expected None, got {result!r}"


def test_returns_none_when_stdout_is_html():
    """When Linear returns an HTML error page (e.g. 5xx), stdout is not JSON.
    Must not raise JSONDecodeError; should return None."""
    html = "<html><body><h1>502 Bad Gateway</h1></body></html>"
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=html, stderr="")
    with mock.patch.object(subprocess, "run", return_value=fake):
        with mock.patch.dict(os.environ, {"LINEAR_API_KEY": "fake-key"}):
            result = sync_comment.linear_comment("AI-2137", "test body")
    assert result is None, f"expected None, got {result!r}"


def test_returns_none_when_graphql_errors_with_null_data():
    """Auth failure: {'data': null, 'errors': [...]} — must not raise TypeError
    on data["data"]["commentCreate"] when data["data"] is None."""
    fake_response = json.dumps({
        "data": None,
        "errors": [{"message": "Authentication required", "extensions": {"code": "AUTHENTICATION_ERROR"}}],
    })
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=fake_response, stderr="")
    with mock.patch.object(subprocess, "run", return_value=fake):
        with mock.patch.dict(os.environ, {"LINEAR_API_KEY": "fake-key"}):
            result = sync_comment.linear_comment("AI-2137", "test body")
    assert result is None, f"expected None, got {result!r}"


def test_returns_none_when_data_is_null_no_errors():
    """Edge case: {'data': null} with no errors key — must not raise."""
    fake_response = json.dumps({"data": None})
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=fake_response, stderr="")
    with mock.patch.object(subprocess, "run", return_value=fake):
        with mock.patch.dict(os.environ, {"LINEAR_API_KEY": "fake-key"}):
            result = sync_comment.linear_comment("AI-2137", "test body")
    assert result is None, f"expected None, got {result!r}"


def test_happy_path_returns_id():
    """When the API succeeds, return the comment id."""
    fake_response = json.dumps({
        "data": {"commentCreate": {"success": True, "comment": {"id": "abc12345-6789"}}}
    })
    fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=fake_response, stderr="")
    with mock.patch.object(subprocess, "run", return_value=fake):
        with mock.patch.dict(os.environ, {"LINEAR_API_KEY": "fake-key"}):
            result = sync_comment.linear_comment("AI-2137", "test body")
    assert result == "abc12345-6789", f"expected comment id, got {result!r}"


if __name__ == "__main__":
    import traceback
    tests = [
        test_returns_none_when_stdout_empty,
        test_returns_none_when_stdout_is_html,
        test_returns_none_when_graphql_errors_with_null_data,
        test_returns_none_when_data_is_null_no_errors,
        test_happy_path_returns_id,
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
