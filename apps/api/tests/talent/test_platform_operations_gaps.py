"""Tests for gaps #181-200: Security, Compliance & Platform Operations."""

from app.talent.services.platform_operations import (
    API_DOCUMENTATION,
    AUDIT_EXPORT_FORMATS,
    DATA_CLASSIFICATION_LEVELS,
    DEFAULT_FEATURE_FLAGS,
    FIELD_CLASSIFICATIONS,
    ISOLATION_CHECKS,
    METERED_OPERATIONS,
    ROLE_HIERARCHY,
    SENSITIVE_OPERATIONS,
    build_health_report,
    build_isolation_test_suite,
    check_ip_allowed,
    check_usage_limit,
    detect_role_escalation,
    format_audit_entry_for_export,
    get_field_classification,
    is_feature_enabled,
    list_feature_flags,
    require_confirmation,
    validate_audit_export_request,
    validate_ip_allowlist,
)


class TestSensitiveOps:
    def test_requires_confirmation(self):
        result = require_confirmation("delete_opportunity", None)
        assert result["required"] is True
        assert "error" in result

    def test_confirmed(self):
        result = require_confirmation("delete_opportunity", "tok123")
        assert result["confirmed"] is True

    def test_non_sensitive(self):
        result = require_confirmation("list_opportunities", None)
        assert result["required"] is False

    def test_operations(self):
        assert len(SENSITIVE_OPERATIONS) >= 7


class TestAuditExport:
    def test_format_entry(self):
        entry = {"created_at": "2026-01-01", "user_id": "u1", "action_type": "create", "target_type": "opportunity", "target_id": "o1"}
        result = format_audit_entry_for_export(entry)
        assert result["action"] == "create"
        assert result["timestamp"] == "2026-01-01"

    def test_validate_format(self):
        assert validate_audit_export_request({"format": "json"}) == []
        assert len(validate_audit_export_request({"format": "xml"})) > 0

    def test_formats(self):
        assert len(AUDIT_EXPORT_FORMATS) == 3


class TestDataClassification:
    def test_email_confidential(self):
        result = get_field_classification("email")
        assert result["level"] >= 2

    def test_capability_public(self):
        result = get_field_classification("capability_name")
        assert result["level"] == 0

    def test_unknown_field(self):
        result = get_field_classification("unknown_field")
        assert result["level"] == 1  # defaults to internal

    def test_levels(self):
        assert len(DATA_CLASSIFICATION_LEVELS) == 4
        assert len(FIELD_CLASSIFICATIONS) >= 10


class TestIPAllowlist:
    def test_valid_ips(self):
        assert validate_ip_allowlist(["192.168.1.1", "10.0.0.0/8"]) == []

    def test_invalid_ip(self):
        errors = validate_ip_allowlist(["not-an-ip"])
        assert len(errors) > 0

    def test_check_allowed(self):
        assert check_ip_allowed("192.168.1.1", ["192.168.1.0/24"]) is True

    def test_check_denied(self):
        assert check_ip_allowed("10.0.0.1", ["192.168.1.0/24"]) is False

    def test_empty_allowlist(self):
        assert check_ip_allowed("1.2.3.4", []) is True


class TestRoleEscalation:
    def test_authorized(self):
        result = detect_role_escalation("member", "admin", "owner")
        assert result["escalation"] is True
        assert result["authorized"] is True
        assert result["blocked"] is False

    def test_blocked(self):
        result = detect_role_escalation("member", "admin", "contributor")
        assert result["blocked"] is True

    def test_no_escalation(self):
        result = detect_role_escalation("admin", "member", "admin")
        assert result["escalation"] is False

    def test_hierarchy(self):
        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["admin"]
        assert len(ROLE_HIERARCHY) >= 4


class TestFeatureFlags:
    def test_enabled(self):
        assert is_feature_enabled("talent_matching") is True

    def test_disabled(self):
        assert is_feature_enabled("gamification") is False

    def test_override(self):
        assert is_feature_enabled("gamification", {"gamification": True}) is True

    def test_unknown(self):
        assert is_feature_enabled("nonexistent") is False

    def test_list(self):
        flags = list_feature_flags()
        assert len(flags) >= 8
        assert all("feature" in f and "enabled" in f for f in flags)

    def test_flags_defined(self):
        assert len(DEFAULT_FEATURE_FLAGS) >= 8


class TestHealthCheck:
    def test_all_healthy(self):
        checks = [
            {"service": "database", "status": "healthy"},
            {"service": "redis", "status": "healthy"},
        ]
        report = build_health_report(checks)
        assert report["overall_status"] == "healthy"

    def test_degraded(self):
        checks = [
            {"service": "database", "status": "healthy"},
            {"service": "redis", "status": "degraded"},
        ]
        report = build_health_report(checks)
        assert report["overall_status"] == "degraded"


class TestUsageMetering:
    def test_within_limit(self):
        result = check_usage_limit(50, 100)
        assert result["within_limit"] is True
        assert result["remaining"] == 50

    def test_exceeded(self):
        result = check_usage_limit(150, 100)
        assert result["within_limit"] is False

    def test_no_limit(self):
        result = check_usage_limit(9999, None)
        assert result["within_limit"] is True

    def test_operations(self):
        assert len(METERED_OPERATIONS) >= 6


class TestIsolation:
    def test_suite_generated(self):
        tests = build_isolation_test_suite()
        assert len(tests) == len(ISOLATION_CHECKS)
        assert all("test_id" in t and "entity" in t for t in tests)


class TestAPIDocumentation:
    def test_structure(self):
        assert API_DOCUMENTATION["title"] == "OpenSkill Studio Talent API"
        assert API_DOCUMENTATION["version"] == "1.0.0"
        assert len(API_DOCUMENTATION["tags"]) >= 8
        assert API_DOCUMENTATION["total_endpoints"] >= 200
