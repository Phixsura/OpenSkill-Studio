from app.services.app_marketplace_extension_template_engine import TemplateEngineService, TemplateError
import pytest


def test_simple_variable():
    eng = TemplateEngineService()
    assert eng.render("Hello {{ name }}!", {"name": "World"}) == "Hello World!"


def test_html_escaping():
    eng = TemplateEngineService()
    result = eng.render("{{ content }}", {"content": "<script>alert('xss')</script>"})
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_raw_unescaped():
    eng = TemplateEngineService()
    result = eng.render("{{{ html }}}", {"html": "<b>bold</b>"})
    assert "<b>bold</b>" in result


def test_nested_property():
    eng = TemplateEngineService()
    result = eng.render("{{ user.name }}", {"user": {"name": "Alice"}})
    assert result == "Alice"


def test_if_block():
    eng = TemplateEngineService()
    tpl = "{% if show %}Visible{% endif %}"
    assert eng.render(tpl, {"show": True}) == "Visible"
    assert eng.render(tpl, {"show": False}) == ""


def test_if_not():
    eng = TemplateEngineService()
    tpl = "{% if not logged_in %}Please login{% endif %}"
    assert eng.render(tpl, {"logged_in": False}) == "Please login"
    assert eng.render(tpl, {"logged_in": True}) == ""


def test_for_loop():
    eng = TemplateEngineService()
    tpl = "{% for item in items %}{{ item }} {% endfor %}"
    result = eng.render(tpl, {"items": ["a", "b", "c"]})
    assert "a" in result and "b" in result and "c" in result


def test_loop_index():
    eng = TemplateEngineService()
    tpl = "{% for x in items %}{{ loop.index }}{% endfor %}"
    result = eng.render(tpl, {"items": ["a", "b", "c"]})
    assert result == "012"


def test_nested_for():
    eng = TemplateEngineService()
    tpl = "{% for g in groups %}{% for u in g.users %}{{ u }} {% endfor %}{% endfor %}"
    ctx = {"groups": [{"users": ["A", "B"]}, {"users": ["C"]}]}
    result = eng.render(tpl, ctx)
    assert "A" in result and "B" in result and "C" in result


def test_filter():
    eng = TemplateEngineService()
    assert eng.render("{{ name|upper }}", {"name": "alice"}) == "ALICE"
    assert eng.render("{{ title|lower }}", {"title": "HELLO"}) == "hello"


def test_missing_variable():
    eng = TemplateEngineService()
    assert eng.render("{{ missing }}", {}) == ""


def test_complex_template():
    eng = TemplateEngineService()
    tpl = """
<h1>{{ title }}</h1>
{% if items %}
<ul>
{% for item in items %}
<li>{{ item.name }}: {{ item.price }}</li>
{% endfor %}
</ul>
{% endif %}
{% if not items %}No items{% endif %}
"""
    result = eng.render(tpl, {
        "title": "Shop",
        "items": [{"name": "Widget", "price": 9.99}, {"name": "Gadget", "price": 19.99}]
    })
    assert "Shop" in result
    assert "Widget" in result
    assert "9.99" in result
    assert "No items" not in result
