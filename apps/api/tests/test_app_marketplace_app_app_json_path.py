from app.services.app_marketplace_app_app_json_path import query_json

DATA = {
    "app": {
        "name": "MyApp",
        "version": "2.0.0",
        "authors": ["Alice", "Bob"],
        "config": {"port": 3000}
    }
}

def test_simple():
    r = query_json(data=DATA, path="$.app.name")
    assert r["found"]
    assert r["value"] == "MyApp"

def test_nested():
    r = query_json(data=DATA, path="app.config.port")
    assert r["value"] == 3000

def test_array_index():
    r = query_json(data=DATA, path="app.authors[1]")
    assert r["value"] == "Bob"

def test_not_found():
    r = query_json(data=DATA, path="app.missing")
    assert not r["found"]
