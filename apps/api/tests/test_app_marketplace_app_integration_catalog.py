from app.services.app_marketplace_app_integration_catalog import list_integrations, connect_integration

def test_list_all():
    r = list_integrations()
    assert r["total"] == 6
    assert len(r["categories"]) >= 4

def test_filter_category():
    r = list_integrations(category="communication")
    assert r["total"] == 1
    assert r["integrations"][0]["id"] == "slack"

def test_search():
    r = list_integrations(search="github")
    assert r["total"] == 1

def test_connect():
    r = connect_integration(app_id="a1", integration_id="slack", config={"channel": "#dev"})
    assert r["success"]
    assert r["integration"] == "Slack"

def test_connect_unknown():
    r = connect_integration(app_id="a1", integration_id="unknown")
    assert not r["success"]
