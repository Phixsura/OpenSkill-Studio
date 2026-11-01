from app.services.app_marketplace_extension_csp_builder import (
    CSPBuilderService,
)
import pytest


def test_create_default_policy():
    svc = CSPBuilderService()
    p = svc.create_policy("ext-1")
    assert "default-src" in p.directives
    assert "'none'" in p.directives["object-src"]


def test_build_header():
    svc = CSPBuilderService()
    svc.create_policy("ext-1")
    h = svc.build_header("ext-1")
    assert h["header"] == "Content-Security-Policy"
    assert "default-src 'self'" in h["value"]


def test_report_only():
    svc = CSPBuilderService()
    svc.create_policy("ext-1", report_only=True)
    h = svc.build_header("ext-1")
    assert h["header"] == "Content-Security-Policy-Report-Only"


def test_block_unsafe_eval():
    svc = CSPBuilderService()
    svc.create_policy("ext-1")
    with pytest.raises(ValueError, match="Dangerous"):
        svc.set_directive("ext-1", "script-src", ["'self'", "'unsafe-eval'"])


def test_allow_dangerous_explicit():
    svc = CSPBuilderService()
    svc.create_policy("ext-1")
    svc.set_directive("ext-1", "script-src", ["'self'", "'unsafe-eval'"],
                      allow_dangerous=True)
    h = svc.build_header("ext-1")
    assert "'unsafe-eval'" in h["value"]


def test_nonce_generation():
    svc = CSPBuilderService()
    svc.create_policy("ext-1")
    nonce = svc.generate_nonce("ext-1")
    assert len(nonce) > 10
    h = svc.build_header("ext-1")
    assert f"'nonce-{nonce}'" in h["value"]


def test_violation_tracking():
    svc = CSPBuilderService()
    svc.create_policy("ext-1")
    svc.report_violation("ext-1", "script-src", "https://evil.com/bad.js")
    violations = svc.get_violations("ext-1")
    assert len(violations) == 1
    summary = svc.get_violation_summary("ext-1")
    assert summary["script-src"] == 1
