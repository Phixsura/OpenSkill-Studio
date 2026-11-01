from app.services.app_marketplace_app_app_app_app_app_app_app_dev_toolkit import generate_test_data, compute_checksum, format_json

def test_generate():
    users = generate_test_data(entity="users", count=3)
    assert len(users) == 3
    assert all("email" in u for u in users)
    apps = generate_test_data(entity="apps", count=2)
    assert len(apps) == 2
    assert all("version" in a for a in apps)

def test_checksum():
    c1 = compute_checksum({"key": "value"})
    c2 = compute_checksum({"key": "value"})
    assert c1 == c2
    assert len(c1) == 16

def test_format():
    r = format_json({"name": "test", "value": 42})
    assert r["lines"] > 1
    assert r["size_bytes"] > 0
    assert '"name"' in r["formatted"]
