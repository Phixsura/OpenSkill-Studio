from app.services.app_marketplace_app_app_app_app_app_app_app_api_doc_gen import generate_docs, generate_curl_examples

def test_docs():
    endpoints = [
        {"path": "/api/v1/users", "method": "GET", "summary": "List users", "tag": "Users"},
        {"path": "/api/v1/users", "method": "POST", "summary": "Create user", "tag": "Users"},
        {"path": "/api/v1/apps", "method": "GET", "summary": "List apps", "tag": "Apps"},
    ]
    r = generate_docs(endpoints, title="OpenSkill API", version="3.0.0")
    assert r["path_count"] == 2
    assert r["operation_count"] == 3
    assert "Users" in r["tags"]
    assert "Apps" in r["tags"]

def test_curl():
    endpoints = [{"path": "/api/v1/users", "method": "GET"}]
    examples = generate_curl_examples(endpoints)
    assert "curl" in examples[0]["curl"]
    assert "Bearer" in examples[0]["curl"]
