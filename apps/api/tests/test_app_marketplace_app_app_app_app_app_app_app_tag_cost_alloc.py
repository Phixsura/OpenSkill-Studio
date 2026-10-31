from app.services.app_marketplace_app_app_app_app_app_app_app_tag_cost_alloc import allocate_by_tags

def test_allocate():
    resources = [
        {"name": "web-1", "cost": 200, "tags": {"team": "platform"}},
        {"name": "web-2", "cost": 200, "tags": {"team": "platform"}},
        {"name": "db-1", "cost": 500, "tags": {"team": "data"}},
        {"name": "misc", "cost": 100, "tags": {}},
    ]
    r = allocate_by_tags(resources, tag_key="team")
    assert r["total_cost"] == 1000
    assert r["group_count"] == 2
    assert r["breakdown"][0]["tag"] == "data"  # highest cost
    assert r["breakdown"][0]["cost"] == 500
    assert r["untagged_cost"] == 100
    assert r["coverage_pct"] == 90.0
