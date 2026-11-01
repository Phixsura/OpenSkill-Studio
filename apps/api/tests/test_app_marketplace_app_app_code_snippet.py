from app.services.app_marketplace_app_app_code_snippet import build_code_snippet

def test_basic():
    code = "def hello():\n    print('hi')"
    r = build_code_snippet(code=code, language="python", title="example.py")
    assert r["line_count"] == 2
    assert r["icon"] == "🐍"
    assert r["title"] == "example.py"
    assert r["lines"][0]["number"] == 1

def test_xss():
    r = build_code_snippet(code="<script>alert(1)</script>", title="<b>bad</b>")
    assert "<script>" not in r["lines"][0]["content"]
    assert "<b>" not in r["title"]
