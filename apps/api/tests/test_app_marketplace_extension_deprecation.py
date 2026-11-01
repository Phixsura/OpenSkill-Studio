from app.services.app_marketplace_extension_deprecation import (
    DeprecationService, DeprecationPhase,
)


def test_announce():
    ds = DeprecationService()
    notice = ds.announce("ext-1", "1.0", "2027-01-01", reason="Replaced by v2",
                          replacement_id="ext-1-v2", migration_guide="Update imports")
    assert notice.phase == DeprecationPhase.ANNOUNCED
    assert notice.replacement_id == "ext-1-v2"


def test_advance_phases():
    ds = DeprecationService()
    ds.announce("ext-2", "1.0", "2027-06-01")
    ok, _ = ds.advance_phase("ext-2", "1.0")
    assert ok
    assert ds.get_notice("ext-2", "1.0").phase == DeprecationPhase.GRACE_PERIOD
    ds.advance_phase("ext-2", "1.0")
    assert ds.get_notice("ext-2", "1.0").phase == DeprecationPhase.SUNSET
    ds.advance_phase("ext-2", "1.0")
    assert ds.get_notice("ext-2", "1.0").phase == DeprecationPhase.REMOVED


def test_cannot_advance_past_removed():
    ds = DeprecationService()
    ds.announce("ext-3", "*", "2027-01-01")
    for _ in range(3):
        ds.advance_phase("ext-3", "*")
    ok, msg = ds.advance_phase("ext-3", "*")
    assert ok is False


def test_notification_tracking():
    ds = DeprecationService()
    ds.announce("ext-4", "1.0", "2027-01-01", affected_orgs=["org-1", "org-2", "org-3"])
    ds.notify_org("ext-4", "1.0", "org-1")
    unnotified = ds.get_unnotified_orgs("ext-4", "1.0")
    assert "org-1" not in unnotified
    assert len(unnotified) == 2


def test_is_deprecated():
    ds = DeprecationService()
    ds.announce("ext-5", "1.0", "2027-01-01")
    assert ds.is_deprecated("ext-5", "1.0") is True
    assert ds.is_deprecated("ext-5", "2.0") is False


def test_active_deprecations():
    ds = DeprecationService()
    ds.announce("ext-6", "1.0", "2027-01-01")
    ds.announce("ext-7", "1.0", "2027-06-01")
    # Remove ext-7
    for _ in range(3):
        ds.advance_phase("ext-7", "1.0")
    active = ds.get_active_deprecations()
    assert len(active) == 1
    assert active[0].extension_id == "ext-6"


def test_migration_info():
    ds = DeprecationService()
    ds.announce("ext-8", "1.0", "2027-03-01", replacement_id="ext-8-v2",
                migration_guide="See docs/migration.md")
    info = ds.get_migration_info("ext-8", "1.0")
    assert info["replacement_id"] == "ext-8-v2"
    assert "migration.md" in info["migration_guide"]
