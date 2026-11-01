from app.services.app_marketplace_extension_versioned_config import (
    VersionedConfigService,
)


def test_save_and_get():
    svc = VersionedConfigService()
    cv = svc.save("ext-1", {"theme": "dark", "lang": "en"}, "admin")
    assert cv.version == 1
    assert svc.get_current("ext-1") == {"theme": "dark", "lang": "en"}


def test_versioning():
    svc = VersionedConfigService()
    svc.save("ext-1", {"v": 1}, "admin")
    svc.save("ext-1", {"v": 2}, "admin")
    svc.save("ext-1", {"v": 3}, "admin")
    assert len(svc.get_history("ext-1")) == 3
    assert svc.get_version("ext-1", 2).data == {"v": 2}


def test_diff():
    svc = VersionedConfigService()
    svc.save("ext-1", {"a": 1, "b": 2}, "admin")
    svc.save("ext-1", {"b": 3, "c": 4}, "admin")
    d = svc.diff("ext-1", 1, 2)
    assert d["added"] == {"c": 4}
    assert d["removed"] == {"a": 1}
    assert d["changed"]["b"] == {"from": 2, "to": 3}
    assert d["has_changes"] is True


def test_no_diff():
    svc = VersionedConfigService()
    svc.save("ext-1", {"x": 1}, "admin")
    svc.save("ext-1", {"x": 1}, "admin")
    d = svc.diff("ext-1", 1, 2)
    assert d["has_changes"] is False


def test_rollback():
    svc = VersionedConfigService()
    svc.save("ext-1", {"theme": "light"}, "admin")
    svc.save("ext-1", {"theme": "dark"}, "admin")
    svc.rollback("ext-1", 1, "admin")
    assert svc.get_current("ext-1") == {"theme": "light"}
    assert len(svc.get_history("ext-1")) == 3  # rollback creates new version


def test_schema_validation():
    svc = VersionedConfigService()
    svc.set_schema("ext-1", {
        "required": ["name"],
        "properties": {"name": {"type": "string"}, "port": {"type": "integer"}},
    })
    result = svc.save("ext-1", {"port": 3000}, "admin")
    assert "error" in result  # missing required "name"


def test_type_validation():
    svc = VersionedConfigService()
    svc.set_schema("ext-1", {"properties": {"count": {"type": "integer"}}})
    result = svc.save("ext-1", {"count": "not_int"}, "admin")
    assert "error" in result
