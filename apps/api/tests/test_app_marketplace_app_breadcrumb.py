from app.services.app_marketplace_app_breadcrumb import build_breadcrumbs

def test_root():
    r = build_breadcrumbs(path="/")
    assert r["depth"] == 1
    assert r["current"] == "Home"

def test_nested():
    r = build_breadcrumbs(path="/apps/my-cool-app/settings")
    assert r["depth"] == 4
    assert r["breadcrumbs"][1]["label"] == "Apps"
    assert r["breadcrumbs"][2]["label"] == "My Cool App"
    assert r["breadcrumbs"][3]["label"] == "Settings"
    assert r["breadcrumbs"][3]["active"]

def test_known_route():
    r = build_breadcrumbs(path="/analytics")
    assert r["current"] == "Analytics"
