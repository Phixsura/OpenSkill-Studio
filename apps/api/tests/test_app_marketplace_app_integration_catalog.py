from app.services.app_marketplace_app_integration_catalog import list_integrations, search_integrations, get_integration

def test_list_all():
    assert len(list_integrations()) == 6

def test_filter_category():
    r = list_integrations(category="communication")
    assert all(i["category"] == "communication" for i in r)

def test_filter_status():
    r = list_integrations(status="beta")
    assert all(i["status"] == "beta" for i in r)

def test_search():
    r = search_integrations(query="slack")
    assert len(r) == 1
    assert r[0]["id"] == "slack"

def test_get():
    r = get_integration(integration_id="github")
    assert r["name"] == "GitHub"

def test_get_missing():
    assert get_integration(integration_id="nope") is None
