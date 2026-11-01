from app.services.app_marketplace_app_app_template_engine import render_template

def test_basic():
    r = render_template(template="Hello, {{ name }}!", variables={"name": "World"})
    assert r["output"] == "Hello, World!"
    assert not r["has_missing"]

def test_filter():
    r = render_template(template="{{ name | upper }}", variables={"name": "alice"})
    assert r["output"] == "ALICE"

def test_missing():
    r = render_template(template="Hi {{ who }}", variables={})
    assert r["has_missing"]
    assert "who" in r["missing"]
    assert "{{ who }}" in r["output"]

def test_escape_filter():
    r = render_template(template="{{ input | escape }}", variables={"input": "<script>"})
    assert "<script>" not in r["output"]
    assert "&lt;" in r["output"]
