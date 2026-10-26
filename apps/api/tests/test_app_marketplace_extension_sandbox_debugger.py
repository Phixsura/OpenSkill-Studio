from app.services.app_marketplace_extension_sandbox_debugger import (
    SandboxDebuggerService, BreakpointType, DebugState,
)
import pytest


def test_start_session():
    svc = SandboxDebuggerService()
    session = svc.start_session("sb-1")
    assert session.state == DebugState.RUNNING
    assert session.session_id.startswith("dbg_")


def test_add_breakpoint():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    bp = svc.add_breakpoint(s.session_id, "index.js", 42)
    assert bp is not None
    assert bp.line == 42
    assert len(s.breakpoints) == 1


def test_invalid_line():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    with pytest.raises(ValueError, match=">= 1"):
        svc.add_breakpoint(s.session_id, "file.js", 0)


def test_hit_breakpoint_pauses():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    bp = svc.add_breakpoint(s.session_id, "app.js", 10)
    stack = [{"function": "main", "file": "app.js", "line": 10, "locals": {"x": 42}}]
    svc.hit_breakpoint(s.session_id, bp.bp_id, stack)
    assert s.state == DebugState.PAUSED
    assert len(s.call_stack) == 1
    assert s.call_stack[0].locals["x"] == 42
    assert bp.hit_count == 1


def test_step_and_resume():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    bp = svc.add_breakpoint(s.session_id, "app.js", 5)
    svc.hit_breakpoint(s.session_id, bp.bp_id, [{"function": "f", "file": "app.js", "line": 5}])
    assert svc.step(s.session_id) is True
    assert s.state == DebugState.STEPPING
    assert svc.resume(s.session_id) is True
    assert s.state == DebugState.RUNNING


def test_evaluate_when_paused():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    bp = svc.add_breakpoint(s.session_id, "a.js", 1)
    svc.hit_breakpoint(s.session_id, bp.bp_id, [{"function": "f", "file": "a.js", "line": 1}])
    result = svc.evaluate(s.session_id, "x + 1")
    assert result["expression"] == "x + 1"
    assert len(s.eval_history) == 1


def test_evaluate_requires_pause():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    result = svc.evaluate(s.session_id, "x")
    assert "error" in result


def test_toggle_and_remove():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    bp = svc.add_breakpoint(s.session_id, "f.js", 10)
    svc.toggle_breakpoint(s.session_id, bp.bp_id)
    assert bp.enabled is False
    svc.remove_breakpoint(s.session_id, bp.bp_id)
    assert len(s.breakpoints) == 0


def test_watch_expressions():
    svc = SandboxDebuggerService()
    s = svc.start_session("sb-1")
    svc.add_watch(s.session_id, "counter", "state.count")
    assert s.watch_expressions["counter"] == "state.count"
