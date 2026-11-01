"""Tests for App Template Renderer — variables, conditionals, loops, escaping."""

import pytest

from app.services.app_template_renderer import AppTemplateRenderer


class TestRegister:
    def test_register(self):
        r = AppTemplateRenderer()
        t = r.register_template("inst-1", "welcome", "Hello {{name}}!")
        assert t.template_id == "welcome"

    def test_missing_content(self):
        r = AppTemplateRenderer()
        with pytest.raises(ValueError, match="content"):
            r.register_template("inst-1", "t1", "")


class TestVariableSubstitution:
    def test_simple(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "Hello {{name}}, welcome to {{app}}!")
        result = r.render("inst-1", "t1", {"name": "Alice", "app": "Studio"})
        assert result.output == "Hello Alice, welcome to Studio!"

    def test_missing_variable(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "Hi {{name}}!")
        result = r.render("inst-1", "t1", {})
        assert result.output == "Hi !"

    def test_dotted_key(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{user.name}}")
        result = r.render("inst-1", "t1", {"user": {"name": "Bob"}})
        assert result.output == "Bob"

    def test_variables_used(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{a}} and {{b}}")
        result = r.render("inst-1", "t1", {"a": "1", "b": "2"})
        assert "a" in result.variables_used
        assert "b" in result.variables_used


class TestHtmlEscaping:
    def test_escapes_by_default(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{content}}")
        result = r.render("inst-1", "t1", {"content": "<script>alert('xss')</script>"})
        assert "<script>" not in result.output
        assert "&lt;script&gt;" in result.output

    def test_no_escape_option(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{content}}")
        result = r.render("inst-1", "t1", {"content": "<b>bold</b>"}, escape_html=False)
        assert "<b>bold</b>" in result.output


class TestConditionals:
    def test_if_truthy(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{#if premium}}Premium user{{/if}}")
        result = r.render("inst-1", "t1", {"premium": True})
        assert result.output == "Premium user"

    def test_if_falsy(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{#if premium}}Premium{{/if}}")
        result = r.render("inst-1", "t1", {"premium": False})
        assert result.output == ""

    def test_if_missing(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{#if x}}shown{{/if}}")
        result = r.render("inst-1", "t1", {})
        assert result.output == ""


class TestLoops:
    def test_each_list(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{#each items}}[{{.}}]{{/each}}")
        result = r.render("inst-1", "t1", {"items": ["a", "b", "c"]}, escape_html=False)
        assert result.output == "[a][b][c]"

    def test_each_objects(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{#each users}}{{name}} {{/each}}")
        result = r.render("inst-1", "t1", {
            "users": [{"name": "Alice"}, {"name": "Bob"}]
        }, escape_html=False)
        assert "Alice" in result.output
        assert "Bob" in result.output

    def test_each_empty(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "{{#each items}}x{{/each}}")
        result = r.render("inst-1", "t1", {"items": []})
        assert result.output == ""


class TestListTemplates:
    def test_list(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "a")
        r.register_template("inst-1", "t2", "b")
        assert len(r.list_templates("inst-1")) == 2


class TestIsolation:
    def test_cross_installation(self):
        r = AppTemplateRenderer()
        r.register_template("inst-1", "t1", "hello")
        with pytest.raises(KeyError):
            r.render("inst-2", "t1", {})
