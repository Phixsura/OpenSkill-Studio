from app.services.app_marketplace_app_environment_switcher import get_environments, switch_environment

def test_get():
    r = get_environments(app_id="a1", current="staging")
    assert r["total"] == 3
    active = next(e for e in r["environments"] if e["active"])
    assert active["id"] == "staging"

def test_switch():
    r = switch_environment(app_id="a1", target="staging")
    assert r["switched_to"] == "staging"

def test_prod_requires_confirm():
    r = switch_environment(app_id="a1", target="production")
    assert "requires_confirm" in r

def test_prod_confirmed():
    r = switch_environment(app_id="a1", target="production", confirm=True)
    assert r["switched_to"] == "production"

def test_unknown():
    r = switch_environment(app_id="a1", target="nope")
    assert "error" in r
