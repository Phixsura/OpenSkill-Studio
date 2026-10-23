from app.services.app_marketplace_app_developer_playground_sharing import create_shared_snippet, fork_snippet, get_trending_snippets

def test_create():
    s = create_shared_snippet(developer_id="d1", code="console.log('hi')", language="javascript", title="Hello World")
    assert len(s["snippet_id"]) == 10
    assert s["views"] == 0

def test_fork():
    s = {"snippet_id": "abc", "developer_id": "d1", "title": "X", "forks": 5, "views": 100}
    f = fork_snippet(snippet=s, developer_id="d2")
    assert f["forked_from"] == "abc"
    assert f["developer_id"] == "d2"

def test_trending():
    snippets = [{"title": "A", "views": 10, "forks": 0}, {"title": "B", "views": 5, "forks": 10},
                {"title": "C", "views": 100, "forks": 1}]
    t = get_trending_snippets(snippets=snippets, limit=2)
    assert t[0]["title"] == "C"  # highest combined score
