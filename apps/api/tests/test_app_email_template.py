"""Tests for App Email Template — register, render, variables, escaping."""

import pytest

from app.services.app_email_template import AppEmailTemplate


class TestRegister:
    def test_register(self):
        t = AppEmailTemplate()
        tpl = t.register("inst-1", "welcome", "Welcome Email",
                          subject="Welcome {{name}}!", body_html="<h1>Hi {{name}}</h1>")
        assert tpl.template_id == "welcome"

    def test_missing_subject(self):
        t = AppEmailTemplate()
        with pytest.raises(ValueError, match="subject"):
            t.register("inst-1", "t1", "X", subject="", body_html="<p>body</p>")


class TestRender:
    def test_basic_render(self):
        t = AppEmailTemplate()
        t.register("inst-1", "welcome", "Welcome",
                    subject="Welcome {{name}}!", body_html="<h1>Hi {{name}}</h1>")
        r = t.render("inst-1", "welcome", "alice@example.com", {"name": "Alice"})
        assert r.subject == "Welcome Alice!"
        assert "Alice" in r.body_html
        assert r.to == "alice@example.com"

    def test_html_escaping(self):
        t = AppEmailTemplate()
        t.register("inst-1", "t1", "Test", subject="Hi", body_html="<p>{{content}}</p>")
        r = t.render("inst-1", "t1", "a@b.com", {"content": "<script>alert('xss')</script>"})
        assert "<script>" not in r.body_html
        assert "&lt;script&gt;" in r.body_html

    def test_missing_variable(self):
        t = AppEmailTemplate()
        t.register("inst-1", "t1", "Test", subject="Hi {{name}}", body_html="<p>body</p>")
        r = t.render("inst-1", "t1", "a@b.com", {})
        assert r.subject == "Hi "

    def test_variables_used(self):
        t = AppEmailTemplate()
        t.register("inst-1", "t1", "Test", subject="{{greeting}} {{name}}", body_html="<p>{{name}}</p>")
        r = t.render("inst-1", "t1", "a@b.com", {"greeting": "Hello", "name": "Bob"})
        assert "greeting" in r.variables_used
        assert "name" in r.variables_used

    def test_missing_to(self):
        t = AppEmailTemplate()
        t.register("inst-1", "t1", "Test", subject="Hi", body_html="<p>x</p>")
        with pytest.raises(ValueError, match="to"):
            t.render("inst-1", "t1", "", {})

    def test_plain_text_fallback(self):
        t = AppEmailTemplate()
        t.register("inst-1", "t1", "Test", subject="Hi", body_html="<p>Hello {{name}}</p>")
        r = t.render("inst-1", "t1", "a@b.com", {"name": "Alice"})
        assert "Alice" in r.body_text


class TestIsolation:
    def test_cross_installation(self):
        t = AppEmailTemplate()
        t.register("inst-1", "t1", "Test", subject="Hi", body_html="<p>x</p>")
        with pytest.raises(KeyError):
            t.render("inst-2", "t1", "a@b.com", {})
