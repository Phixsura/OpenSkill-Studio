from app.services.app_marketplace_app_app_app_similar_apps import find_similar_apps

def test_similar():
    app = {"id": "a1", "tags": ["editor", "code"], "category": "tools"}
    catalog = [
        {"id": "a2", "name": "Code Linter", "tags": ["code", "lint"], "category": "tools", "rating": 4.5},
        {"id": "a3", "name": "Chat App", "tags": ["chat"], "category": "communication", "rating": 4.0},
        {"id": "a4", "name": "IDE", "tags": ["editor", "code"], "category": "tools", "rating": 4.8},
    ]
    r = find_similar_apps(app=app, catalog=catalog)
    assert r["total_found"] == 2  # a2 and a4 (a3 has no overlap)
    assert r["similar"][0]["name"] == "IDE"  # highest score (2 tag matches + category)

def test_no_similar():
    r = find_similar_apps(app={"id": "x", "tags": ["unique"], "category": "rare"}, catalog=[])
    assert r["total_found"] == 0
