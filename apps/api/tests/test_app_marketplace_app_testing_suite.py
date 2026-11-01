from app.services.app_marketplace_app_testing_suite import run_test_suite

def test_all_pass():
    manifest = {"name": "MyApp", "version": "1.0.0",
        "description": "A fantastic app that does amazing things",
        "icon": "icon.png", "permissions": ["read"], "entry_point": "index.ts"}
    r = run_test_suite(app_id="a1", manifest=manifest)
    assert r["all_passed"]
    assert r["score"] == 100

def test_partial():
    manifest = {"name": "App", "version": "1.0.0", "description": "Short",
        "entry_point": "main.py"}
    r = run_test_suite(app_id="a1", manifest=manifest)
    assert not r["all_passed"]
    assert r["passed"] < r["total"]

def test_empty():
    r = run_test_suite(app_id="a1", manifest={})
    assert r["score"] < 50
    assert not r["ready_to_publish"]
