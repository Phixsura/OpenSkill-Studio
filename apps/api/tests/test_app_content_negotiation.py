"""Tests for App Content Negotiation — register, negotiate, fallback."""

import pytest

from app.services.app_content_negotiation import AppContentNegotiation


class TestRegister:
    def test_register(self):
        n = AppContentNegotiation()
        f = n.register_format("inst-1", "application/json")
        assert f.quality == 1.0

    def test_invalid_quality(self):
        n = AppContentNegotiation()
        with pytest.raises(ValueError):
            n.register_format("inst-1", "application/json", quality=0)


class TestNegotiate:
    def test_exact_match(self):
        n = AppContentNegotiation()
        n.register_format("inst-1", "application/json")
        n.register_format("inst-1", "application/xml")
        result = n.negotiate("inst-1", "application/xml")
        assert result.media_type == "application/xml"
        assert result.matched is True

    def test_wildcard(self):
        n = AppContentNegotiation()
        n.register_format("inst-1", "application/json")
        result = n.negotiate("inst-1", "*/*")
        assert result.matched is True

    def test_quality_preference(self):
        n = AppContentNegotiation()
        n.register_format("inst-1", "application/json", quality=0.9)
        n.register_format("inst-1", "application/xml", quality=0.5)
        result = n.negotiate("inst-1", "application/json, application/xml")
        assert result.media_type == "application/json"

    def test_fallback(self):
        n = AppContentNegotiation()
        n.register_format("inst-1", "application/json")
        result = n.negotiate("inst-1", "text/html")
        assert result.media_type == "application/json"
        assert result.matched is False

    def test_empty_formats(self):
        n = AppContentNegotiation()
        result = n.negotiate("inst-1", "application/json")
        assert result.media_type == "application/json"
        assert result.matched is False


class TestIsolation:
    def test_cross(self):
        n = AppContentNegotiation()
        n.register_format("inst-1", "application/xml")
        assert n.list_formats("inst-2") == []
