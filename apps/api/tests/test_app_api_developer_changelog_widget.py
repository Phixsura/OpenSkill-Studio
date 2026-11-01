import pytest
from app.services.app_api_developer_changelog_widget import AppAPIDeveloperChangelogWidget

class TestWidget:
    def test_configure(self):
        w = AppAPIDeveloperChangelogWidget()
        widget = w.configure("inst-1", "w1", "bottom-right", "bell", 10)
        assert widget.position == "bottom-right"

    def test_ctr(self):
        w = AppAPIDeveloperChangelogWidget()
        w.configure("inst-1", "w1")
        for _ in range(100): w.record_impression("inst-1")
        for _ in range(5): w.record_click("inst-1")
        assert w.get_widget("inst-1").ctr == 5.0

    def test_invalid_position(self):
        w = AppAPIDeveloperChangelogWidget()
        with pytest.raises(ValueError):
            w.configure("inst-1", "w1", "center")

    def test_not_configured(self):
        w = AppAPIDeveloperChangelogWidget()
        with pytest.raises(KeyError):
            w.get_widget("inst-1")
