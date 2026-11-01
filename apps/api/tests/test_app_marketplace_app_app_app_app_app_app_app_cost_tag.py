from app.services.app_marketplace_app_app_app_app_app_app_app_cost_tag import tag_cost

def test_tag():
    r = tag_cost([
        {"name": "api", "cost": 500, "tags": {"cost_center": "engineering"}},
        {"name": "db", "cost": 300, "tags": {"cost_center": "engineering"}},
        {"name": "test-vm", "cost": 100, "tags": {}},
    ])
    assert r["by_cost_center"]["engineering"] == 800
    assert r["untagged_cost"] == 100
    assert r["tagged_pct"] == 89
