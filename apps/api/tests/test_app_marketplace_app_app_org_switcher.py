from app.services.app_marketplace_app_app_org_switcher import build_org_switcher

def test_switcher():
    orgs = [
        {"id": "o1", "name": "Acme Corp", "role": "owner", "plan": "pro"},
        {"id": "o2", "name": "Side Project", "role": "admin", "plan": "free"},
    ]
    r = build_org_switcher(orgs=orgs, current_org_id="o1")
    assert r["total"] == 2
    assert r["current"]["name"] == "Acme Corp"
    assert r["current"]["initials"] == "AC"
    assert r["can_create"]
