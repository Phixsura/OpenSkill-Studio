"""Full manifest validation — valid manifests with all features."""

from app.services.manifest_validator import validate_manifest


def test_connector_manifest():
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "LMS Connector", "slug": "lms-conn", "version": "2.1.0", "category": "connector"},
        "permissions": ["read:cohorts", "read:submissions", "write:project_results", "subscribe:events"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60,
            "network": {"allowed_hosts": ["api.lms.example.com"], "egress_policy": "allowlist"}},
        "event_subscriptions": ["submission.completed", "submission.graded"],
        "secrets": [{"key": "LMS_API_KEY", "required": True}, {"key": "LMS_SECRET"}],
        "config_schema": {"type": "object", "properties": {"base_url": {"type": "string"}}, "required": ["base_url"]},
    })
    assert r.valid, f"Errors: {r.errors}"
    assert r.warnings == []


def test_ui_extension_manifest():
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Dashboard Widget", "slug": "dash-widget", "version": "1.0.0", "category": "ui_extension"},
        "permissions": ["read:cohorts", "read:projects", "extend:ui"],
        "ui_extensions": [
            {"surface": "dashboard_card", "title": "Progress Card", "entry": "card.html", "viewport": {"width": 400, "height": 300}},
            {"surface": "project_sidebar", "title": "Project Info", "entry": "sidebar.html"},
        ],
    })
    assert r.valid, f"Errors: {r.errors}"


def test_automation_manifest():
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Auto Grader", "slug": "auto-grader", "version": "1.0.0", "category": "automation"},
        "permissions": ["read:submissions", "write:evaluations", "subscribe:events", "run:background_jobs"],
        "sandbox": {"runtime": "nodejs20", "memory_mb": 128, "timeout_seconds": 30},
        "event_subscriptions": ["submission.completed"],
    })
    assert r.valid, f"Errors: {r.errors}"


def test_analytics_manifest():
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Skill Analytics", "slug": "skill-analytics", "version": "1.0.0", "category": "analytics"},
        "permissions": ["read:cohorts", "read:skills", "read:skill_progress", "read:analytics", "export:analytics"],
    })
    assert r.valid, f"Errors: {r.errors}"


def test_ecosystem_source_manifest():
    r = validate_manifest({
        "schema_version": "1.0",
        "app": {"name": "Job Board Source", "slug": "job-board", "version": "1.0.0", "category": "ecosystem_source"},
        "permissions": ["read:talent", "write:talent"],
        "sandbox": {"runtime": "python3.11", "memory_mb": 64, "timeout_seconds": 120,
            "network": {"allowed_hosts": ["api.jobboard.com"], "egress_policy": "allowlist"}},
        "secrets": [{"key": "BOARD_API_KEY", "required": True}],
    })
    assert r.valid, f"Errors: {r.errors}"
