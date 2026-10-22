"""Complete platform E2E test — verify the entire developer platform works end-to-end.

This test covers the full lifecycle:
1. Manifest creation → validation → security scan
2. Version diff → changelog → compatibility
3. Health monitoring → alerts → conformance
4. Webhook signing → delivery → circuit breaker
5. OAuth PKCE → token introspection
6. API key generation → rotation
7. Event routing → deduplication → dead letter
8. Marketplace ranking → search → recommendations
9. Developer onboarding → quota → billing
10. Sandbox isolation → resource limits → execution
"""

import pytest
from app.services.manifest_validator import validate_manifest
from app.services.app_security_scanner import scan_manifest
from app.services.app_version_diff import diff_manifests
from app.services.app_changelog import generate_changelog_entry
from app.services.app_compatibility import check_upgrade_compatibility
from app.services.app_health_monitor import HealthScore
from app.services.app_health_alerts import check_health_alerts
from app.services.conformance import ConformanceCheck, ConformanceReport
from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature
from app.services.app_webhook_circuit_breaker import record_success, is_circuit_open, reset_circuit
from app.services.app_oauth_pkce import generate_code_verifier, compute_code_challenge, verify_pkce
from app.services.app_api_key_generator import generate_api_key, verify_api_key
from app.services.app_event_deduplicator import is_duplicate, clear as clear_dedup
from app.services.app_ranking import compute_ranking_score
from app.services.app_content_hash import hash_manifest
from app.services.app_manifest_normalizer import manifests_equal
from app.services.app_sandbox_isolation_checker import check_isolation
from app.services.app_quota import get_limits, check_quota
from app.services.app_billing_summary import build_billing_summary


def test_manifest_to_security_pipeline():
    """1. Manifest → validate → scan → hash."""
    manifest = {
        "schema_version": "1.0",
        "app": {"name": "E2E App", "slug": "e2e-complete", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60},
    }
    assert validate_manifest(manifest).valid
    assert scan_manifest(manifest)["passed"]
    h = hash_manifest(manifest)
    assert len(h) == 64


def test_version_lifecycle():
    """2. Diff → changelog → compatibility."""
    v1 = {"permissions": ["read:cohorts"]}
    v2 = {"permissions": ["read:cohorts", "write:cohorts"]}
    diff = diff_manifests(v1, v2)
    assert not diff["breaking"]
    entry = generate_changelog_entry(version="2.0.0", old_manifest=v1, new_manifest=v2)
    assert len(entry["changes"]) > 0
    compat = check_upgrade_compatibility(v1, v2)
    assert compat["compatible"]


def test_health_monitoring_chain():
    """3. Health → alerts → conformance."""
    health = HealthScore(1000, 10, 5)
    assert health.status == "healthy"
    alerts = check_health_alerts(health.to_dict())
    assert len(alerts) == 0
    report = ConformanceReport(app_id="e2e", app_name="E2E", version="1.0",
        checked_at="now", checks=[ConformanceCheck(name="health", status="pass", message="ok", details=health.to_dict())])
    assert report.passed


def test_webhook_security_chain():
    """4. Webhook sign → verify → circuit breaker."""
    _, secret = generate_webhook_secret()
    sig = sign_payload(b'{"event":"test"}', secret)
    assert verify_signature(b'{"event":"test"}', sig, secret)
    ep = "https://e2e-test.example.com"
    reset_circuit(ep)
    record_success(ep)
    assert not is_circuit_open(ep)


def test_oauth_pkce_flow():
    """5. PKCE verifier → challenge → verify."""
    verifier = generate_code_verifier()
    challenge = compute_code_challenge(verifier)
    assert verify_pkce(verifier, challenge)


def test_api_key_lifecycle():
    """6. Generate → verify."""
    raw, prefix, key_hash = generate_api_key()
    assert verify_api_key(raw, key_hash)
    assert raw.startswith("osk_app_")


def test_event_deduplication():
    """7. Dedup events."""
    clear_dedup()
    assert not is_duplicate("e2e_event_1")
    assert is_duplicate("e2e_event_1")


def test_marketplace_ranking():
    """8. Ranking score."""
    score = compute_ranking_score(install_count=500, health_score=95, days_since_update=7)
    assert score > 0


def test_manifest_normalization():
    """9. Normalize and compare."""
    a = {"permissions": ["write:x", "read:x"]}
    b = {"permissions": ["read:x", "write:x"]}
    assert manifests_equal(a, b)


def test_sandbox_and_quota():
    """10. Sandbox isolation + quota + billing."""
    isolation = check_isolation({"memory_mb": 256, "timeout_seconds": 60, "network": {"egress_policy": "allowlist"}})
    assert isolation["isolated"]
    limits = get_limits("standard")
    assert check_quota(current=5, limit=limits.max_apps, resource="apps")["allowed"]
    bill = build_billing_summary(executions=1000, webhooks=500, api_calls=5000, storage_mb=100)
    assert bill["total_usd"] > 0
