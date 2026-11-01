from app.services.app_marketplace_extension_dep_lock import ExtensionDepLockService


def test_lock_and_verify():
    svc = ExtensionDepLockService()
    svc.lock("ext-1", [{"name": "react", "version": "18.0"}, {"name": "lodash", "version": "4.17"}])
    result = svc.verify("ext-1")
    assert result["verified"] is True
    assert result["total"] == 2


def test_drift_in_sync():
    svc = ExtensionDepLockService()
    deps = [{"name": "react", "version": "18.0"}]
    svc.lock("ext-1", deps)
    drift = svc.check_drift("ext-1", deps)
    assert drift["in_sync"] is True


def test_drift_detected():
    svc = ExtensionDepLockService()
    svc.lock("ext-1", [{"name": "react", "version": "18.0"}, {"name": "lodash", "version": "4.17"}])
    drift = svc.check_drift("ext-1", [
        {"name": "react", "version": "19.0"},  # changed
        {"name": "axios", "version": "1.0"},    # added
    ])
    assert drift["in_sync"] is False
    assert "react" in drift["changed"]
    assert "axios" in drift["added"]
    assert "lodash" in drift["removed"]


def test_integrity_hash():
    svc = ExtensionDepLockService()
    locked = svc.lock("ext-1", [{"name": "pkg", "version": "1.0"}])
    assert locked[0].integrity.startswith("sha256-")


def test_lockfile_hash():
    svc = ExtensionDepLockService()
    svc.lock("ext-1", [{"name": "a", "version": "1"}, {"name": "b", "version": "2"}])
    h = svc.get_lockfile_hash("ext-1")
    assert len(h) == 20
