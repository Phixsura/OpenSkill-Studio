import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_api_developer_api_status_badge import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge

class TestStatusBadge:
    def test_create(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge()
        badge = b.create("inst-1", "b1", "status", "ok", "green")
        assert badge.color == "green"

    def test_uptime_badge(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge()
        badge = b.generate_uptime_badge("inst-1", 99.95)
        assert badge.color == "green"
        assert "99.95%" in badge.value

    def test_build_badge(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge()
        badge = b.generate_build_badge("inst-1", False)
        assert badge.color == "red"
        assert badge.value == "failing"

    def test_render_svg(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge()
        b.create("inst-1", "b1", "api", "v2", "blue")
        svg = b.render_svg("inst-1", "b1")
        assert "<svg" in svg
        assert "#007ec6" in svg

    def test_isolation(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge()
        b.create("inst-1", "b1", "x", "y", "green")
        assert len(b.all_badges("inst-2")) == 0

    def test_svg_xss_escape(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge()
        b.create("inst-1", "b1", '<script>alert("xss")</script>', "val", "green")
        svg = b.render_svg("inst-1", "b1")
        assert "<script>" not in svg
        assert "&lt;script&gt;" in svg
