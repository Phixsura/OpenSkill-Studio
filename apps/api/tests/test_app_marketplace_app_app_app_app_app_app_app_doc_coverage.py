from app.services.app_marketplace_app_app_app_app_app_app_app_doc_coverage import measure_coverage

def test_full():
    r = measure_coverage([
        {"description": True, "examples": True, "params_documented": True, "errors_documented": True},
        {"description": True, "examples": True, "params_documented": True, "errors_documented": True},
    ])
    assert r["overall_pct"] == 100.0
    assert r["grade"] == "A"

def test_partial():
    r = measure_coverage([
        {"description": True, "examples": False, "params_documented": True, "errors_documented": False},
        {"description": False, "examples": False, "params_documented": False, "errors_documented": False},
    ])
    assert r["grade"] in ("C", "F")
    assert r["scores"]["description"] == 50.0
