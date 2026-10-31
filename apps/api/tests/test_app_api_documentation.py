"""Tests for App API Documentation — pages, sections, search."""

import pytest

from app.services.app_api_documentation import AppAPIDocumentation


class TestCreate:
    def test_create(self):
        d = AppAPIDocumentation()
        p = d.create_page("inst-1", "p1", "Getting Started", "# Welcome", "guides")
        assert p.section == "guides"


class TestContent:
    def test_update(self):
        d = AppAPIDocumentation()
        d.create_page("inst-1", "p1", "Guide", "Old content")
        p = d.update_content("inst-1", "p1", "New content")
        assert p.content == "New content"

    def test_view_count(self):
        d = AppAPIDocumentation()
        d.create_page("inst-1", "p1", "Guide", "Content")
        d.record_view("inst-1", "p1")
        d.record_view("inst-1", "p1")
        p = d.list_pages("inst-1")[0]
        assert p.view_count == 2


class TestQuery:
    def test_by_section(self):
        d = AppAPIDocumentation()
        d.create_page("inst-1", "p1", "Auth", "Content", "auth")
        d.create_page("inst-1", "p2", "Users", "Content", "api")
        assert len(d.list_pages("inst-1", section="auth")) == 1

    def test_search(self):
        d = AppAPIDocumentation()
        d.create_page("inst-1", "p1", "Authentication", "How to authenticate")
        d.create_page("inst-1", "p2", "Webhooks", "Configure webhooks")
        results = d.search("inst-1", "auth")
        assert len(results) == 1

    def test_sections(self):
        d = AppAPIDocumentation()
        d.create_page("inst-1", "p1", "A", "C", "guides")
        d.create_page("inst-1", "p2", "B", "C", "api")
        assert d.sections("inst-1") == ["api", "guides"]


class TestIsolation:
    def test_cross(self):
        d = AppAPIDocumentation()
        d.create_page("inst-1", "p1", "Guide", "Content")
        assert d.list_pages("inst-2") == []
