from app.services.app_marketplace_app_app_search_highlight import highlight_matches, extract_snippet

def test_highlight():
    r = highlight_matches(text="Hello World, hello again!", query="hello")
    assert r["match_count"] == 2
    assert "<mark>" in r["highlighted"]

def test_empty_query():
    r = highlight_matches(text="Hello", query="")
    assert r["match_count"] == 0

def test_xss():
    r = highlight_matches(text="<script>alert(1)</script>", query="script")
    # Raw <script> tag must not appear — only escaped entities
    assert "<script>" not in r["highlighted"]
    assert "&lt;" in r["highlighted"]

def test_snippet():
    text = "A " * 100 + "KEYWORD" + " B" * 100
    r = extract_snippet(text=text, query="KEYWORD", context_chars=20)
    assert r["found"]
    assert "KEYWORD" in r["snippet"]

def test_snippet_not_found():
    r = extract_snippet(text="Hello world", query="zzz")
    assert not r["found"]
