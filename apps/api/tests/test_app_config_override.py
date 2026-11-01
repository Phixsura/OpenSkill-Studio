"""Tests for App Config Override — layers, resolution, priority."""

import pytest

from app.services.app_config_override import AppConfigOverride


class TestSetLayer:
    def test_set(self):
        c = AppConfigOverride()
        l = c.set_layer("inst-1", "base", 0, {"timeout": 30, "debug": False})
        assert l.layer_id == "base"
        assert l.values["timeout"] == 30

    def test_replace(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"a": 1})
        c.set_layer("inst-1", "base", 0, {"a": 2})
        assert c.get_value("inst-1", "a") == 2

    def test_missing_id(self):
        c = AppConfigOverride()
        with pytest.raises(ValueError):
            c.set_layer("inst-1", "", 0, {})


class TestRemoveLayer:
    def test_remove(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"a": 1})
        assert c.remove_layer("inst-1", "base") is True
        assert c.get_value("inst-1", "a") is None

    def test_remove_nonexistent(self):
        c = AppConfigOverride()
        assert c.remove_layer("inst-1", "nope") is False


class TestGetValue:
    def test_single_layer(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"port": 8080})
        assert c.get_value("inst-1", "port") == 8080

    def test_higher_priority_wins(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"port": 8080, "debug": False})
        c.set_layer("inst-1", "env", 10, {"debug": True})
        assert c.get_value("inst-1", "debug") is True
        assert c.get_value("inst-1", "port") == 8080

    def test_default_value(self):
        c = AppConfigOverride()
        assert c.get_value("inst-1", "missing", default=42) == 42

    def test_three_layers(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"a": 1, "b": 2, "c": 3})
        c.set_layer("inst-1", "env", 10, {"b": 20, "c": 30})
        c.set_layer("inst-1", "override", 20, {"c": 300})
        assert c.get_value("inst-1", "a") == 1
        assert c.get_value("inst-1", "b") == 20
        assert c.get_value("inst-1", "c") == 300


class TestResolve:
    def test_resolve(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"a": 1, "b": 2})
        c.set_layer("inst-1", "env", 10, {"b": 20, "c": 30})
        resolved = c.resolve("inst-1")
        assert resolved == {"a": 1, "b": 20, "c": 30}

    def test_empty(self):
        c = AppConfigOverride()
        assert c.resolve("inst-1") == {}


class TestListLayers:
    def test_sorted_by_priority(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {})
        c.set_layer("inst-1", "env", 10, {})
        c.set_layer("inst-1", "override", 5, {})
        layers = c.list_layers("inst-1")
        assert [l.layer_id for l in layers] == ["env", "override", "base"]


class TestIsolation:
    def test_cross_installation(self):
        c = AppConfigOverride()
        c.set_layer("inst-1", "base", 0, {"x": 1})
        assert c.get_value("inst-2", "x") is None
