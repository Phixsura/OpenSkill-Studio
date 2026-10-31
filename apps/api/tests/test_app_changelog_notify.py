"""Tests for App Changelog Notify — templates, delivery, tracking."""

import pytest

from app.services.app_changelog_notify import AppChangelogNotify


class TestTemplate:
    def test_register(self):
        n = AppChangelogNotify()
        t = n.register_template("inst-1", "t1", "email", "New Release: {{version}}", "Check out v{{version}}")
        assert t.channel == "email"

    def test_missing_id(self):
        n = AppChangelogNotify()
        with pytest.raises(ValueError):
            n.register_template("inst-1", "", "email", "sub", "body")


class TestNotify:
    def test_notify(self):
        n = AppChangelogNotify()
        n.register_template("inst-1", "t1", "email", "sub", "body")
        ds = n.notify_release("inst-1", "2.0.0", ["alice@x.com", "bob@x.com"], "t1")
        assert len(ds) == 2
        assert ds[0].version == "2.0.0"

    def test_unknown_template(self):
        n = AppChangelogNotify()
        with pytest.raises(KeyError):
            n.notify_release("inst-1", "1.0", ["a@b.com"], "nope")


class TestDeliveries:
    def test_get_all(self):
        n = AppChangelogNotify()
        n.register_template("inst-1", "t1", "email", "s", "b")
        n.notify_release("inst-1", "1.0", ["a@b.com"], "t1")
        n.notify_release("inst-1", "2.0", ["c@d.com"], "t1")
        ds = n.get_deliveries("inst-1")
        assert len(ds) == 2

    def test_filter_version(self):
        n = AppChangelogNotify()
        n.register_template("inst-1", "t1", "email", "s", "b")
        n.notify_release("inst-1", "1.0", ["a@b.com"], "t1")
        n.notify_release("inst-1", "2.0", ["c@d.com"], "t1")
        ds = n.get_deliveries("inst-1", version="1.0")
        assert len(ds) == 1

    def test_count(self):
        n = AppChangelogNotify()
        n.register_template("inst-1", "t1", "email", "s", "b")
        n.notify_release("inst-1", "1.0", ["a@b.com", "c@d.com"], "t1")
        assert n.delivery_count("inst-1") == 2


class TestIsolation:
    def test_cross_installation(self):
        n = AppChangelogNotify()
        n.register_template("inst-1", "t1", "email", "s", "b")
        n.notify_release("inst-1", "1.0", ["a@b.com"], "t1")
        assert n.delivery_count("inst-2") == 0
