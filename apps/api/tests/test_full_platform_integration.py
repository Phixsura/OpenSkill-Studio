"""Full platform integration — manifest → validate → scan → review → diff → changelog → deploy."""

from app.services.manifest_validator import validate_manifest
from app.services.app_security_scanner import scan_manifest
from app.services.app_review_validator import run_automated_review
from app.services.app_version_diff import diff_manifests
from app.services.app_changelog import generate_changelog_entry, format_changelog_markdown
from app.services.app_content_hash import hash_manifest
from app.services.app_health_monitor import HealthScore
from app.services.app_health_alerts import check_health_alerts
from app.services.app_migration_planner import create_migration_plan, validate_migration


def test_end_to_end_app_lifecycle():
    """Simulate complete app lifecycle: create → validate → scan → review → upgrade → monitor."""
    # 1. Create v1 manifest
    v1 = {
        "schema_version": "1.0",
        "app": {"name": "E2E App", "slug": "e2e-app", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30},
    }
    assert validate_manifest(v1).valid
    assert scan_manifest(v1)["passed"]

    # 2. Review v1
    h1 = hash_manifest(v1)
    review1 = run_automated_review(manifest=v1, content_hash=h1, version="1.0.0")
    assert review1["passed"]

    # 3. Create v2 with new features
    v2 = {
        "schema_version": "1.0",
        "app": {"name": "E2E App", "slug": "e2e-app", "version": "2.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts", "subscribe:events"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60},
        "event_subscriptions": ["submission.completed"],
    }
    assert validate_manifest(v2).valid

    # 4. Diff versions
    diff = diff_manifests(v1, v2)
    assert not diff["breaking"]
    assert "write:cohorts" in diff["permissions"]["added"]

    # 5. Generate changelog
    entry = generate_changelog_entry(version="2.0.0", old_manifest=v1, new_manifest=v2, changelog_text="Added write + events")
    md = format_changelog_markdown([entry])
    assert "2.0.0" in md

    # 6. Plan migration
    plan = create_migration_plan(from_version="1.0.0", to_version="2.0.0", old_manifest=v1, new_manifest=v2, installation_count=50)
    assert plan["requires_consent"]
    assert validate_migration(plan)["safe"]

    # 7. Monitor health
    health = HealthScore(1000, 10, 5)
    assert health.status == "healthy"
    alerts = check_health_alerts(health.to_dict())
    assert len(alerts) == 0  # healthy = no alerts
