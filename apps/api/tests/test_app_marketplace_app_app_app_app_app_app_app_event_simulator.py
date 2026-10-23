from app.services.app_marketplace_app_app_app_app_app_app_app_event_simulator import list_templates, generate_event, simulate_delivery

def test_templates():
    t = list_templates()
    assert len(t) == 5
    assert any(x["event_type"] == "app.installed" for x in t)

def test_generate():
    e = generate_event("app.installed", overrides={"plan": "pro"})
    assert e["type"] == "app.installed"
    assert e["payload"]["plan"] == "pro"
    assert e["test"]

def test_simulate():
    e = generate_event("user.created")
    d = simulate_delivery(e, url="https://example.com/hook")
    assert d["success"]
    assert d["test"]
