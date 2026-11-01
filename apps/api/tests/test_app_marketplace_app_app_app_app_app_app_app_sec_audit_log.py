from app.services.app_marketplace_app_app_app_app_app_app_app_sec_audit_log import (
    log_security_event, query_audit_log, audit_summary, clear_audit_log,
)

def test_log_query():
    clear_audit_log()
    log_security_event("alice", "login", "/auth", "success", "1.2.3.4")
    log_security_event("bob", "login_failed", "/auth", "failure", "5.6.7.8")
    log_security_event("alice", "api_call", "/api/users")
    r = query_audit_log(actor="alice")
    assert r["total"] == 2
    r2 = query_audit_log(severity="high")
    assert r2["total"] == 1
    clear_audit_log()

def test_summary():
    clear_audit_log()
    log_security_event("a", "login", "/auth")
    log_security_event("b", "login_failed", "/auth")
    s = audit_summary()
    assert s["total"] == 2
    assert s["by_severity"]["high"] == 1
    clear_audit_log()
