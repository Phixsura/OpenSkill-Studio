from app.services.app_api_docs_builder import build_endpoint_docs, build_docs_toc

EPS = [
    {"method": "GET", "path": "/cohorts", "summary": "List cohorts", "scopes": ["read:cohorts"]},
    {"method": "POST", "path": "/cohorts", "summary": "Create cohort", "scopes": ["write:cohorts"]},
    {"method": "GET", "path": "/apps", "summary": "List apps"},
]

def test_build_docs():
    docs = build_endpoint_docs(EPS)
    assert len(docs) == 3
    assert docs[0]["method"] == "GET"
    assert "curl" in docs[0]["example_curl"]

def test_post_has_body():
    docs = build_endpoint_docs(EPS)
    post = next(d for d in docs if d["method"] == "POST")
    assert "Content-Type" in post["example_curl"]

def test_toc():
    toc = build_docs_toc(EPS)
    resources = {t["resource"] for t in toc}
    assert "cohorts" in resources
    assert "apps" in resources

def test_toc_grouped():
    toc = build_docs_toc(EPS)
    cohorts = next(t for t in toc if t["resource"] == "cohorts")
    assert len(cohorts["endpoints"]) == 2
