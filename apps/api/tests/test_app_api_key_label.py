"""Tests for App API Key Label — register, label, search."""

import pytest
from app.services.app_api_key_label import AppAPIKeyLabel


class TestRegister:
    def test_register(self):
        l = AppAPIKeyLabel()
        k = l.register_key("inst-1", "k1", "Prod Key", ["production", "api"])
        assert k.labels == {"production", "api"}

    def test_duplicate(self):
        l = AppAPIKeyLabel()
        l.register_key("inst-1", "k1", "A")
        with pytest.raises(ValueError):
            l.register_key("inst-1", "k1", "B")


class TestLabels:
    def test_add_remove(self):
        l = AppAPIKeyLabel()
        l.register_key("inst-1", "k1", "Key")
        l.add_labels("inst-1", "k1", ["prod", "v2"])
        l.remove_labels("inst-1", "k1", ["v2"])
        k = l.list_keys("inst-1")[0]
        assert k.labels == {"prod"}

    def test_find_by_label(self):
        l = AppAPIKeyLabel()
        l.register_key("inst-1", "k1", "A", ["prod"])
        l.register_key("inst-1", "k2", "B", ["staging"])
        assert len(l.find_by_label("inst-1", "prod")) == 1

    def test_all_labels(self):
        l = AppAPIKeyLabel()
        l.register_key("inst-1", "k1", "A", ["prod", "api"])
        l.register_key("inst-1", "k2", "B", ["staging"])
        assert l.all_labels("inst-1") == ["api", "prod", "staging"]


class TestIsolation:
    def test_cross(self):
        l = AppAPIKeyLabel()
        l.register_key("inst-1", "k1", "A", ["prod"])
        assert l.list_keys("inst-2") == []
