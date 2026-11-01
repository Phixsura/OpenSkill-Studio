from app.services.app_marketplace_app_app_app_app_app_app_app_api_docs_gen import generate_docs, coverage_report

def test_generate():
    r = generate_docs([
        {"path": "/users", "method": "GET", "summary": "List users", "tag": "users"},
        {"path": "/users", "method": "POST", "summary": "Create user", "tag": "users"},
        {"path": "/orders", "method": "GET", "summary": "List orders", "tag": "orders"},
    ], title="MyAPI", version="2.0")
    assert r["total_endpoints"] == 3
    assert len(r["tags"]) == 2
    assert "get" in r["paths"]["/users"]

def test_coverage():
    r = coverage_report([
        {"path": "/a", "summary": "doc", "example": True},
        {"path": "/b", "summary": "doc"},
        {"path": "/c"},
    ])
    assert r["doc_coverage_pct"] == 66.7
    assert r["example_coverage_pct"] == 33.3
