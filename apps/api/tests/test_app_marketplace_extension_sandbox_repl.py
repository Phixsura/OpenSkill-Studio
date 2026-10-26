from app.services.app_marketplace_extension_sandbox_repl import (
    SandboxReplService,
)


def test_create_and_execute():
    svc = SandboxReplService()
    s = svc.create_session("sb-1", "node20")
    result = svc.execute(s.session_id, "1 + 2")
    assert result.output == "=> 1 + 2"
    assert result.error == ""


def test_variable_assignment():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    svc.execute(s.session_id, "let x = 42")
    result = svc.execute(s.session_id, "x")
    assert result.output == "42"


def test_dangerous_code_blocked():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    result = svc.execute(s.session_id, "import os")
    assert "Blocked" in result.error


def test_empty_input():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    result = svc.execute(s.session_id, "   ")
    assert "Empty" in result.error


def test_code_too_long():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    result = svc.execute(s.session_id, "x" * 10001)
    assert "too long" in result.error


def test_history():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    svc.execute(s.session_id, "a")
    svc.execute(s.session_id, "b")
    history = svc.get_history(s.session_id)
    assert len(history) == 2


def test_completions():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    svc.execute(s.session_id, "let counter = 0")
    svc.execute(s.session_id, "let config = {}")
    completions = svc.get_completions(s.session_id, "con")
    assert "config" in completions
    assert "console.log" in completions


def test_clear_context():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    svc.execute(s.session_id, "let x = 1")
    svc.clear_context(s.session_id)
    assert len(s.context) == 0


def test_end_session():
    svc = SandboxReplService()
    s = svc.create_session("sb-1")
    assert svc.end_session(s.session_id) is True
    assert svc.end_session(s.session_id) is False
