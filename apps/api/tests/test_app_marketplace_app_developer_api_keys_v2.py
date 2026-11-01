from app.services.app_marketplace_app_developer_api_keys_v2 import create_api_key_v2, is_key_expired, get_key_usage_summary

def test_create():
    k = create_api_key_v2(app_id="a1", name="prod", scopes=["read", "write"])
    assert k["raw_key"].startswith("osk_")
    assert k["expires_at"] is None

def test_with_expiry():
    k = create_api_key_v2(app_id="a1", name="temp", scopes=["read"], expires_in_days=30)
    assert k["expires_at"] is not None

def test_not_expired():
    k = create_api_key_v2(app_id="a1", name="x", scopes=[], expires_in_days=365)
    assert not is_key_expired(key=k)

def test_expired():
    assert is_key_expired(key={"expires_at": "2020-01-01T00:00:00+00:00"})

def test_summary():
    keys = [{"usage_count": 100, "expires_at": None}, {"usage_count": 50, "expires_at": "2020-01-01T00:00:00+00:00"}]
    s = get_key_usage_summary(keys=keys)
    assert s["active"] == 1
    assert s["expired"] == 1
    assert s["total_usage"] == 150
