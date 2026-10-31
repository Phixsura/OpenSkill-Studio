from app.services.app_marketplace_app_app_app_app_app_app_app_req_fingerprint import fingerprint, group_by_fingerprint

def test_fingerprint():
    f1 = fingerprint("GET", "/api/users")
    f2 = fingerprint("GET", "/api/users")
    assert f1["fingerprint"] == f2["fingerprint"]
    f3 = fingerprint("POST", "/api/users")
    assert f3["fingerprint"] != f1["fingerprint"]

def test_group():
    r = group_by_fingerprint([
        {"method": "GET", "path": "/api/users"},
        {"method": "GET", "path": "/api/users"},
        {"method": "POST", "path": "/api/orders", "body": '{"a":1}'},
    ])
    assert r["unique_fingerprints"] == 2
    assert r["duplicate_groups"] == 1
    assert r["dedup_savings_pct"] == 33.3
