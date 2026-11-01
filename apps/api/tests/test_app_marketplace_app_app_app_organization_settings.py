from app.services.app_marketplace_app_app_app_organization_settings import build_org_settings

def test_settings():
    org = {"org_name": "Acme Corp", "slug": "acme", "two_factor": True, "plan": "pro"}
    r = build_org_settings(org=org)
    assert r["group_count"] == 3
    assert r["org_name"] == "Acme Corp"
    general = r["groups"][0]
    assert general["id"] == "general"
    assert general["count"] == 3
