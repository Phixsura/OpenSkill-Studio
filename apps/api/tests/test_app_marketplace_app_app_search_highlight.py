from app.services.app_marketplace_app_app_search_highlight import highlight_matches, extract_snippet

def test_highlight():
    r = highlight_matches(text="Hello World, hello again!", query="hello")
    assert r["match_count"] == 2
    assert "<mark>" in r["highlighted"]
    assert "Hello" in r["highlighted"]

def test_empty_query():
    r = highlight_matches(text="Hello", query="")
    assert r["match_count"] == 0

def test_xss():
    r = highlight_matches(text="<script>alert(1)</script>", query="script")
    assert "<script>" not in r["highlighted"]
    assert "assert "&lt;script&gt;" in r["highlighted"]lt;" in r["highlighted"]  # entities preserved

def test_snippet():
    text = "A " * 100 + "KEYWORD" + " B" * 100
    r = extract_snippet(text=text, query="KEYWORD", context_chars=20)
    assert r["found"]
    assert "KEYWORD" in r["snippet"]
    assert len(r["snippet"]) < len(text)

def test_snippet_not_found():
    r = extract_snippet(text="Hello world", query="zzz")
    assert not r["found"]
