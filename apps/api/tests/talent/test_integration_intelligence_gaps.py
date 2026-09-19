"""Tests for gaps #171-180: Integration & API Intelligence."""

from app.talent.services.integration_intelligence import (
    API_KEY_SCOPES,
    ENDPOINT_RATE_LIMITS,
    HRIS_EMPLOYEE_SCHEMA,
    SUPPORTED_ATS_PROVIDERS,
    SUPPORTED_HRIS_PROVIDERS,
    build_slack_message,
    build_verification_response,
    generate_api_key,
    get_endpoint_limit,
    list_slack_event_mappings,
    validate_api_key_scopes,
    validate_ats_config,
    validate_hris_employee,
    verify_api_key,
)


class TestAPIKeys:
    def test_generate(self):
        result = generate_api_key("org1", "Test Key", ["read:capabilities"])
        assert result["raw_key"].startswith("osk_")
        assert len(result["key_hash"]) == 64
        assert result["key_prefix"] == result["raw_key"][:12]

    def test_verify_valid(self):
        result = generate_api_key("org1", "K", ["read:capabilities"])
        assert verify_api_key(result["raw_key"], result["key_hash"]) is True

    def test_verify_invalid(self):
        result = generate_api_key("org1", "K", ["read:capabilities"])
        assert verify_api_key("wrong_key", result["key_hash"]) is False

    def test_validate_scopes_valid(self):
        assert validate_api_key_scopes(["read:capabilities", "write:evidence"]) == []

    def test_validate_scopes_invalid(self):
        errors = validate_api_key_scopes(["read:capabilities", "invalid:scope"])
        assert len(errors) > 0

    def test_validate_scopes_empty(self):
        errors = validate_api_key_scopes([])
        assert len(errors) > 0

    def test_scope_count(self):
        assert len(API_KEY_SCOPES) >= 10


class TestHRIS:
    def test_valid_employee(self):
        emp = {
            "employee_id": "E001",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@test.com",
        }
        assert validate_hris_employee(emp) == []

    def test_missing_fields(self):
        errors = validate_hris_employee({"first_name": "Alice"})
        assert len(errors) >= 2

    def test_invalid_email(self):
        errors = validate_hris_employee(
            {"employee_id": "1", "first_name": "A", "last_name": "B", "email": "invalid"}
        )
        assert any("email" in e.lower() for e in errors)

    def test_providers(self):
        assert "workday" in SUPPORTED_HRIS_PROVIDERS
        assert "bamboohr" in SUPPORTED_HRIS_PROVIDERS
        assert len(SUPPORTED_HRIS_PROVIDERS) >= 8

    def test_schema_structure(self):
        assert "required" in HRIS_EMPLOYEE_SCHEMA
        assert "properties" in HRIS_EMPLOYEE_SCHEMA


class TestATS:
    def test_valid_config(self):
        config = {
            "provider": "greenhouse",
            "api_url": "https://api.greenhouse.io",
            "sync_direction": "inbound",
            "sync_entities": ["jobs", "candidates"],
        }
        assert validate_ats_config(config) == []

    def test_invalid_provider(self):
        errors = validate_ats_config(
            {"provider": "invalid", "api_url": "https://x.com", "sync_direction": "inbound"}
        )
        assert len(errors) > 0

    def test_invalid_direction(self):
        errors = validate_ats_config(
            {"provider": "greenhouse", "api_url": "https://x.com", "sync_direction": "wrong"}
        )
        assert len(errors) > 0

    def test_providers(self):
        assert "lever" in SUPPORTED_ATS_PROVIDERS
        assert len(SUPPORTED_ATS_PROVIDERS) >= 6


class TestSlack:
    def test_build_message(self):
        msg = build_slack_message(
            "application.submitted", {"candidate": "Alice", "role": "AI Designer"}
        )
        assert msg is not None
        assert "Alice" in msg["text"]
        assert msg["channel"] == "#hiring"

    def test_unknown_event(self):
        assert build_slack_message("unknown.event", {}) is None

    def test_list_events(self):
        events = list_slack_event_mappings()
        assert "application.submitted" in events
        assert len(events) >= 4


class TestWebhookVerification:
    def test_build_response(self):
        resp = build_verification_response("ep1", "HMAC-SHA256")
        assert resp["signing_algorithm"] == "HMAC-SHA256"
        assert "ep1" in resp["verification_url"]


class TestEndpointRateLimits:
    def test_get_specific(self):
        limit = get_endpoint_limit("POST", "/talent/resume/parse")
        assert limit is not None
        assert limit["limit"] == 10

    def test_get_unknown(self):
        assert get_endpoint_limit("GET", "/unknown") is None

    def test_limits_defined(self):
        assert len(ENDPOINT_RATE_LIMITS) >= 5
