from app.services.app_marketplace_app_developer_app_documentation_generator import generate_endpoint_docs, generate_docs_markdown, compute_doc_coverage

def test_generate_docs():
    endpoints = [{"method": "GET", "path": "/users", "summary": "List users", "description": "Get all users"}]
    r = generate_endpoint_docs(endpoints=endpoints)
    assert len(r) == 1
    assert r[0]["title"] == "List users"

def test_markdown():
    docs = [{"method": "GET", "path": "/users", "description": "List all", "auth_required": True, "parameters": [{"name": "limit", "type": "int"}]}]
    md = generate_docs_markdown(app_name="MyApp", docs=docs)
    assert "# MyApp API Reference" in md
    assert "GET `/users`" in md

def test_coverage():
    r = compute_doc_coverage(total_endpoints=10, documented_endpoints=8)
    assert r["coverage_pct"] == 80.0
    assert not r["fully_documented"]
