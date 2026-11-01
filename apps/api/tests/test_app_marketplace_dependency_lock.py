from app.services.app_marketplace_dependency_lock import DependencyLockService


DEPS = [
    {"name": "sdk", "version": "3.0.0"},
    {"name": "lodash", "version": "4.17.21"},
    {"name": "react", "version": "18.2.0"},
]


def test_create_lock():
    dls = DependencyLockService()
    lock = dls.create_lock("ext-1", DEPS)
    assert lock.lock_version == 1
    assert len(lock.dependencies) == 3
    assert len(lock.checksum) == 16


def test_verify_match():
    dls = DependencyLockService()
    dls.create_lock("ext-2", DEPS)
    ok, errors = dls.verify("ext-2", DEPS)
    assert ok is True


def test_verify_version_mismatch():
    dls = DependencyLockService()
    dls.create_lock("ext-3", DEPS)
    modified = [{"name": "sdk", "version": "4.0.0"}, {"name": "lodash", "version": "4.17.21"}, {"name": "react", "version": "18.2.0"}]
    ok, errors = dls.verify("ext-3", modified)
    assert ok is False
    assert any("version mismatch" in e for e in errors)


def test_verify_missing_dep():
    dls = DependencyLockService()
    dls.create_lock("ext-4", DEPS)
    partial = [{"name": "sdk", "version": "3.0.0"}]
    ok, errors = dls.verify("ext-4", partial)
    assert ok is False
    assert any("Missing" in e for e in errors)


def test_diff():
    dls = DependencyLockService()
    dls.create_lock("ext-5", DEPS)
    new_deps = [{"name": "sdk", "version": "4.0.0"}, {"name": "react", "version": "18.2.0"}, {"name": "axios", "version": "1.0.0"}]
    diff = dls.diff("ext-5", new_deps)
    assert "axios" in diff["added"]
    assert "lodash" in diff["removed"]
    assert "sdk" in diff["changed"]


def test_history():
    dls = DependencyLockService()
    dls.create_lock("ext-6", DEPS)
    dls.create_lock("ext-6", [{"name": "sdk", "version": "4.0.0"}])
    history = dls.get_history("ext-6")
    assert len(history) == 2
    assert history[1].lock_version == 2
