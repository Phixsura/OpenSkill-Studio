import pytest
from app.services.app_api_developer_api_api_developer_api_api_platform_release_notes import AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes

class TestPlatformReleaseNotes:
    def test_create(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes()
        n = r.create("inst-1", "v2.0", "Major Release", "New features", highlights=["New API", "Better docs"])
        assert len(n.highlights) == 2

    def test_publish(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes()
        r.create("inst-1", "v1.0", "First", "Initial release")
        n = r.publish("inst-1", "v1.0")
        assert n.published is True

    def test_latest(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes()
        r.create("inst-1", "v1.0", "First", "A")
        r.create("inst-1", "v2.0", "Second", "B")
        r.publish("inst-1", "v1.0")
        r.publish("inst-1", "v2.0")
        assert r.latest("inst-1").version == "v2.0"

    def test_with_breaking(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes()
        r.create("inst-1", "v1.0", "Safe", "No breaks")
        r.create("inst-1", "v2.0", "Breaking", "Big changes", breaking_changes=["Removed /old"])
        assert len(r.with_breaking("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes()
        r.create("inst-1", "v1.0", "A", "B")
        assert len(r.all_notes("inst-2")) == 0
