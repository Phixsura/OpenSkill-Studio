from app.services.app_api_developer_platform_sdk_api_platform_developer_api_changelog_generator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGenerator, ChangeEntry,
)

class TestChangelogGenerator:
    def test_markdown_generation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGenerator()
        svc.add_entry("inst-1", ChangeEntry(change_id="c1", version="v2.0", change_type="added", description="New users endpoint", endpoints=["/users"]))
        svc.add_entry("inst-1", ChangeEntry(change_id="c2", version="v2.0", change_type="removed", description="Dropped legacy auth", breaking=True))
        md = svc.generate_markdown("inst-1", "v2.0")
        assert "New users endpoint" in md
        assert "**BREAKING**" in md
        assert "/users" in md

    def test_rss_escaping(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGenerator()
        svc.add_entry("inst-1", ChangeEntry(change_id="c1", version="v1.0", change_type="fixed", description='Fix <script>alert("xss")</script>'))
        rss = svc.generate_rss_item("inst-1", "v1.0")
        assert "<script>" not in rss
        assert "&lt;script&gt;" in rss

    def test_breaking_changes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGenerator()
        svc.add_entry("inst-1", ChangeEntry(change_id="c1", version="v2.0", change_type="removed", description="Removed /old", breaking=True))
        svc.add_entry("inst-1", ChangeEntry(change_id="c2", version="v2.0", change_type="added", description="Added /new"))
        assert len(svc.breaking_changes("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGenerator()
        svc.add_entry("inst-1", ChangeEntry(change_id="c1", version="v1.0", change_type="added", description="test"))
        assert svc.versions("inst-2") == []
