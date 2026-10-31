from app.services.app_marketplace_app_app_app_app_app_app_app_tag_policy import enforce_policy

def test_enforce():
    r = enforce_policy([
        {"name": "api", "tags": {"environment": "prod", "team": "platform", "cost_center": "eng", "service": "api", "managed_by": "terraform"}},
        {"name": "db", "tags": {"environment": "prod", "team": "data"}},
    ])
    assert r["compliant"] == 1
    assert r["non_compliant"] == 1
    assert r["compliance_pct"] == 50
    assert len(r["violations"][0]["missing_tags"]) == 3
