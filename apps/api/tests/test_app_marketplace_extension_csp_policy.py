from app.services.app_marketplace_extension_csp_policy import (
    CSPPolicyManager, CSPDirectives,
)


def test_default_policy():
    csp = CSPPolicyManager()
    header = csp.generate_header("ext-1")
    assert "default-src 'self'" in header
    assert "script-src 'self'" in header
    assert "object-src 'none'" in header


def test_custom_policy():
    csp = CSPPolicyManager()
    csp.set_policy("ext-2", CSPDirectives(
        script_src=["'self'", "https://cdn.example.com"],
        connect_src=["'self'", "https://api.example.com"],
    ))
    header = csp.generate_header("ext-2")
    assert "cdn.example.com" in header
    assert "api.example.com" in header


def test_add_allowed_source():
    csp = CSPPolicyManager()
    assert csp.add_allowed_source("ext-3", "connect_src", "https://hooks.slack.com") is True
    header = csp.generate_header("ext-3")
    assert "hooks.slack.com" in header


def test_blocklist():
    csp = CSPPolicyManager()
    csp.add_to_blocklist("https://evil.com")
    assert csp.add_allowed_source("ext-4", "script_src", "https://evil.com") is False


def test_remove_source():
    csp = CSPPolicyManager()
    csp.add_allowed_source("ext-5", "img_src", "https://images.test.com")
    csp.remove_allowed_source("ext-5", "img_src", "https://images.test.com")
    header = csp.generate_header("ext-5")
    assert "images.test.com" not in header


def test_validate_source():
    csp = CSPPolicyManager()
    csp.set_policy("ext-6", CSPDirectives(frame_src=["'none'"]))
    assert csp.validate_source("ext-6", "frame_src", "https://any.com") is False
    assert csp.validate_source("ext-6", "default_src", "'self'") is True
