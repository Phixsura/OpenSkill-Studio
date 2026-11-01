from app.services.app_marketplace_app_app_app_app_app_app_app_cmd_palette import register_commands, search_commands

def test_register():
    r = register_commands([
        {"id": "deploy", "label": "Deploy App", "category": "ops", "keywords": ["ship"]},
        {"id": "settings", "label": "Open Settings", "category": "nav"},
        {"id": "logout", "label": "Log Out", "category": "auth"},
    ])
    assert r["total"] == 3
    assert r["by_category"]["ops"] == 1

def test_search():
    reg = register_commands([
        {"id": "deploy", "label": "Deploy App", "keywords": ["ship", "release"]},
        {"id": "settings", "label": "Open Settings", "keywords": ["config"]},
    ])
    results = search_commands(reg, "deploy")
    assert len(results) == 1
    assert results[0]["id"] == "deploy"
    results2 = search_commands(reg, "config")
    assert len(results2) == 1
    assert results2[0]["id"] == "settings"
