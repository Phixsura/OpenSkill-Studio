from app.services.app_marketplace_extension_csp_engine import CspEngineService


def test_create_policy_with_base():
    svc = CspEngineService()
    policy = svc.create_policy("ext-1")
    rendered = svc.render("ext-1")
    assert "default-src 'self'" in rendered
    assert "object-src 'none'" in rendered


def test_add_valid_source():
    svc = CspEngineService()
    svc.create_policy("ext-1")
    ok, msg = svc.add_source("ext-1", "script-src", "https://cdn.example.com")
    assert ok is True
    assert "cdn.example.com" in svc.render("ext-1")


def test_reject_unsafe_in_strict():
    svc = CspEngineService()
    svc.create_policy("ext-1", strict=True)
    ok, msg = svc.add_source("ext-1", "script-src", "'unsafe-inline'")
    assert ok is False
    assert "blocked in strict" in msg


def test_allow_unsafe_in_non_strict():
    svc = CspEngineService()
    svc.create_policy("ext-1", strict=False)
    ok, _ = svc.add_source("ext-1", "script-src", "'unsafe-inline'")
    assert ok is True


def test_reject_invalid_source():
    svc = CspEngineService()
    svc.create_policy("ext-1")
    ok, msg = svc.add_source("ext-1", "script-src", "javascript:alert(1)")
    assert ok is False


def test_reject_invalid_directive():
    svc = CspEngineService()
    svc.create_policy("ext-1")
    ok, msg = svc.add_source("ext-1", "not-a-directive", "'self'")
    assert ok is False


def test_nonce_generation():
    svc = CspEngineService()
    svc.create_policy("ext-1")
    nonce = svc.generate_nonce("ext-1")
    assert nonce is not None
    rendered = svc.render("ext-1")
    assert f"'nonce-{nonce}'" in rendered


def test_violation_tracking():
    svc = CspEngineService()
    svc.create_policy("ext-1")
    svc.report_violation("ext-1", "script-src", "https://evil.com/inject.js")
    svc.report_violation("ext-1", "script-src", "https://evil.com/inject.js")
    svc.report_violation("ext-1", "img-src", "https://tracker.com/pixel.gif")
    summary = svc.get_violation_summary("ext-1")
    assert summary["total"] == 3
    assert summary["by_directive"]["script-src"] == 2
    assert summary["top_blocked"]["https://evil.com/inject.js"] == 2


def test_no_duplicate_sources():
    svc = CspEngineService()
    svc.create_policy("ext-1")
    svc.add_source("ext-1", "connect-src", "https://api.example.com")
    svc.add_source("ext-1", "connect-src", "https://api.example.com")
    rendered = svc.render("ext-1")
    assert rendered.count("api.example.com") == 1
