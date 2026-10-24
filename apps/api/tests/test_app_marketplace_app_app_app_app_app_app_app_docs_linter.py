from app.services.app_marketplace_app_app_app_app_app_app_app_docs_linter import lint_endpoint, lint_api

def test_valid():
    r = lint_endpoint({"path": "/users", "method": "GET", "description": "List users",
                        "responses": {"200": "OK"}, "parameters": [{"name": "page", "description": "Page num"}]})
    assert r["valid"]
    assert r["issue_count"] == 0

def test_issues():
    r = lint_endpoint({"path": "/users", "method": "POST", "parameters": [{"name": "id"}]})
    assert not r["valid"]
    assert r["errors"] >= 2  # no description, no responses

def test_lint_api():
    r = lint_api([
        {"path": "/a", "method": "GET", "description": "x", "responses": {"200": "OK"}},
        {"path": "/b", "method": "POST"},
    ])
    assert r["valid"] == 1
    assert r["doc_score"] == 50
