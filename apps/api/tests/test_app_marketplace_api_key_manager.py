from app.services.app_marketplace_api_key_manager import (
    issue_key, validate_key, revoke_key, rotate_key,
    list_keys, check_scope,
)


def test_issue_and_validate():
    result = issue_key("dev-001", "My App Key", ["read", "write"])
    assert result["api_key"].startswith("osk_")
    assert result["active"] is True
    record = validate_key(result["api_key"])
    assert record is not None
    assert record["usage_count"] == 1


def test_revoke():
    result = issue_key("dev-002", "Temp Key", ["read"])
    assert revoke_key(result["api_key"]) is True
    assert validate_key(result["api_key"]) is None


def test_rotate():
    result = issue_key("dev-003", "Rotate Me", ["read", "write"], rate_limit=500)
    old_key = result["api_key"]
    new_result = rotate_key(old_key)
    assert new_result is not None
    assert new_result["api_key"] != old_key
    assert validate_key(old_key) is None  # old revoked
    assert validate_key(new_result["api_key"]) is not None  # new works


def test_list_keys():
    issue_key("dev-010", "Key A", ["read"])
    issue_key("dev-010", "Key B", ["write"])
    keys = list_keys("dev-010")
    assert len(keys) >= 2
    assert all(k["developer_id"] == "dev-010" for k in keys)


def test_check_scope():
    result = issue_key("dev-020", "Scoped", ["read", "analytics"])
    assert check_scope(result["api_key"], "read") is True
    assert check_scope(result["api_key"], "admin") is False


def test_wildcard_scope():
    result = issue_key("dev-030", "Admin", ["*"])
    assert check_scope(result["api_key"], "anything") is True
