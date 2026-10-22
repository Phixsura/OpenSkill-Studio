from app.services.app_docs_index import get_docs_tree, search_docs

def test_tree():
    tree = get_docs_tree()
    assert len(tree) >= 3

def test_search():
    r = search_docs("typescript")
    assert any("TypeScript" in p["title"] for p in r)

def test_search_empty():
    assert search_docs("nonexistent") == []
