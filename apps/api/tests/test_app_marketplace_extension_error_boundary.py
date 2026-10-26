from app.services.app_marketplace_extension_error_boundary import (
    ErrorBoundaryService, ErrorCategory, ErrorAction,
)


def test_handle_runtime_error():
    svc = ErrorBoundaryService()
    err = svc.handle_error("ext-1", "TypeError: undefined is not a function",
                           ErrorCategory.RUNTIME)
    assert err.category == ErrorCategory.RUNTIME
    assert err.action_taken == ErrorAction.SKIP


def test_transient_retry():
    svc = ErrorBoundaryService()
    err = svc.handle_error("ext-1", "Connection timeout", ErrorCategory.TIMEOUT)
    assert err.action_taken == ErrorAction.RETRY


def test_fallback():
    svc = ErrorBoundaryService()
    svc.register_fallback("ext-1", "get_data", {"data": [], "fallback": True})
    err = svc.handle_error("ext-1", "DB error", ErrorCategory.RUNTIME,
                           function_name="get_data")
    assert err.action_taken == ErrorAction.FALLBACK
    fb = svc.get_fallback("ext-1", "get_data")
    assert fb["fallback"] is True


def test_circuit_breaker():
    svc = ErrorBoundaryService()
    for i in range(10):
        svc.handle_error("ext-1", f"Error {i}", ErrorCategory.RUNTIME)
    assert svc.is_circuit_open("ext-1") is True
    err = svc.handle_error("ext-1", "Another error")
    assert err.action_taken == ErrorAction.HALT


def test_reset_circuit():
    svc = ErrorBoundaryService()
    for i in range(10):
        svc.handle_error("ext-1", f"err {i}")
    assert svc.reset_circuit("ext-1") is True
    assert svc.is_circuit_open("ext-1") is False


def test_category_filter():
    svc = ErrorBoundaryService()
    svc.handle_error("ext-1", "timeout", ErrorCategory.TIMEOUT)
    svc.handle_error("ext-1", "oom", ErrorCategory.MEMORY)
    svc.handle_error("ext-1", "timeout2", ErrorCategory.TIMEOUT)
    errors = svc.get_errors("ext-1", category=ErrorCategory.TIMEOUT)
    assert len(errors) == 2


def test_summary():
    svc = ErrorBoundaryService()
    svc.handle_error("ext-1", "a", ErrorCategory.RUNTIME)
    svc.handle_error("ext-1", "b", ErrorCategory.TIMEOUT)
    summary = svc.get_summary("ext-1")
    assert summary["total"] == 2
    assert summary["by_category"]["runtime"] == 1


def test_resolve():
    svc = ErrorBoundaryService()
    err = svc.handle_error("ext-1", "bug")
    assert svc.resolve(err.error_id) is True
    assert err.resolved is True
