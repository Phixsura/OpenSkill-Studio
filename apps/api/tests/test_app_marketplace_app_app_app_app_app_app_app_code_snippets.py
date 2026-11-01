from app.services.app_marketplace_app_app_app_app_app_app_app_code_snippets import CodeSnippetManager

def test_snippets():
    mgr = CodeSnippetManager()
    s1 = mgr.create(title="Auth middleware", language="python",
                      code="def auth(req): ...", tags=["auth", "middleware"])
    s2 = mgr.create(title="React hook", language="typescript",
                      code="const useAuth = () => {}", tags=["react", "hooks"])
    results = mgr.search("auth")
    assert len(results) == 1  # only "Auth middleware" matches
    r = mgr.copy(s1["id"])
    assert r["copies"] == 1
    by_lang = mgr.list_by_language()
    assert by_lang["python"] == 1
    assert by_lang["typescript"] == 1
