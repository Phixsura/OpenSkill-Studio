from app.services.app_marketplace_app_app_api_docs_page import build_docs_page

def test_docs():
    r = build_docs_page()
    assert r["total_endpoints"] == 8
    assert len(r["sections"]) == 3
    assert r["sections"][1]["title"] == "Apps"
    assert r["sections"][1]["endpoint_count"] == 5
    assert r["version"] == "v1"
