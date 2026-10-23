from app.services.app_marketplace_code_snippet_library import list_snippets, get_snippet

def test_list():
    r = list_snippets()
    assert r["total"] == 2
    assert len(r["categories"]) >= 1

def test_filter():
    r = list_snippets(category="webhooks")
    assert r["total"] == 1

def test_get():
    r = get_snippet(snippet_id="install_app", language="python")
    assert "openskill" in r["code"]
    assert "<" not in r["html_safe_code"] or "&lt;" in r["html_safe_code"]

def test_not_found():
    r = get_snippet(snippet_id="nope", language="python")
    assert "error" in r
