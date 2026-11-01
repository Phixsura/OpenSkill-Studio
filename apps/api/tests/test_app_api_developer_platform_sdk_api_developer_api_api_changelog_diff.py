import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_api_changelog_diff import AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff

class TestChangelogDiff:
    def test_create(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff()
        diff = d.create_diff("inst-1", "v1", "v2", [
            {"change_type": "added", "target": "GET /api/v2/users", "description": "New users endpoint"},
            {"change_type": "removed", "target": "GET /api/v1/users", "description": "Removed old endpoint"},
        ])
        assert diff.breaking_count == 1
        assert diff.additions == 1
        assert diff.is_breaking is True

    def test_non_breaking(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff()
        diff = d.create_diff("inst-1", "v1", "v1.1", [
            {"change_type": "added", "target": "GET /api/v1/stats", "description": "New stats"},
        ])
        assert diff.is_breaking is False

    def test_invalid_type(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff()
        with pytest.raises(ValueError):
            d.create_diff("inst-1", "v1", "v2", [{"change_type": "hacked", "target": "x", "description": "y"}])

    def test_breaking_diffs(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff()
        d.create_diff("inst-1", "v1", "v2", [{"change_type": "removed", "target": "/old", "description": "x"}])
        d.create_diff("inst-1", "v2", "v3", [{"change_type": "added", "target": "/new", "description": "y"}])
        assert len(d.breaking_diffs("inst-1")) == 1

    def test_isolation(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff()
        d.create_diff("inst-1", "v1", "v2", [])
        assert len(d.all_diffs("inst-2")) == 0
