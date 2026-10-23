from app.services.app_marketplace_app_app_app_app_app_app_app_api_key_display import generate_api_key, mask_key, format_key_list

def test_generate():
    k = generate_api_key(prefix="sk_test")
    assert k["key"].startswith("sk_test_")
    assert k["prefix"] == "sk_test"
    assert "•" in k["display"]

def test_mask():
    assert len(mask_key("sk_live_abc123def456")) == 20  # 8 shown + 12 masked
    assert mask_key("short") == "•••••"

def test_format():
    keys = [{"name": "Production", "key": "sk_live_abc123def456", "scopes": ["read", "write"]}]
    r = format_key_list(keys)
    assert len(r) == 1
    assert r[0]["name"] == "Production"
    assert "•" in r[0]["masked"]
