"""Tests for App API Mock — add, match, hit counts."""

import pytest

from app.services.app_api_mock import AppAPIMock


class TestAddMock:
    def test_add(self):
        m = AppAPIMock()
        mock = m.add_mock("inst-1", "m1", "GET", "/api/users", body='[{"id":"u1"}]')
        assert mock.method == "GET"
        assert mock.status_code == 200

    def test_duplicate(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api")
        with pytest.raises(ValueError):
            m.add_mock("inst-1", "m1", "POST", "/api")


class TestMatch:
    def test_match(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api/users")
        result = m.match("inst-1", "GET", "/api/users")
        assert result is not None
        assert result.mock_id == "m1"

    def test_no_match(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api/users")
        assert m.match("inst-1", "POST", "/api/users") is None

    def test_case_insensitive_method(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "get", "/api")
        assert m.match("inst-1", "GET", "/api") is not None

    def test_hit_count(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api")
        m.match("inst-1", "GET", "/api")
        m.match("inst-1", "GET", "/api")
        assert m.get_mock("inst-1", "m1").hit_count == 2


class TestRemove:
    def test_remove(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api")
        assert m.remove_mock("inst-1", "m1") is True
        assert m.list_mocks("inst-1") == []


class TestReset:
    def test_reset_counts(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api")
        m.match("inst-1", "GET", "/api")
        m.reset_counts("inst-1")
        assert m.get_mock("inst-1", "m1").hit_count == 0


class TestIsolation:
    def test_cross_installation(self):
        m = AppAPIMock()
        m.add_mock("inst-1", "m1", "GET", "/api")
        assert m.match("inst-2", "GET", "/api") is None
