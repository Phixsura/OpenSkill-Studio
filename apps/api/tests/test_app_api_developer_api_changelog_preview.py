import pytest
from app.services.app_api_developer_api_changelog_preview import AppAPIDeveloperAPIChangelogPreview

class TestPreview:
    def test_create(self):
        p = AppAPIDeveloperAPIChangelogPreview()
        pr = p.create("inst-1", "p1", "v3.0", "Major Release", ["Dark mode", "API v2"])
        assert len(pr.entries) == 2
        assert pr.published is False

    def test_approve_publish(self):
        p = AppAPIDeveloperAPIChangelogPreview()
        p.create("inst-1", "p1", "v3.0", "Release", ["Entry"])
        p.approve("inst-1", "p1", "alice")
        pr = p.publish("inst-1", "p1")
        assert pr.published is True

    def test_publish_without_approval(self):
        p = AppAPIDeveloperAPIChangelogPreview()
        p.create("inst-1", "p1", "v3.0", "Release", ["Entry"])
        with pytest.raises(ValueError, match="approved"):
            p.publish("inst-1", "p1")

    def test_drafts(self):
        p = AppAPIDeveloperAPIChangelogPreview()
        p.create("inst-1", "p1", "v3.0", "A", ["E1"])
        p.create("inst-1", "p2", "v3.1", "B", ["E2"])
        p.approve("inst-1", "p1", "bob")
        p.publish("inst-1", "p1")
        assert len(p.drafts("inst-1")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperAPIChangelogPreview()
        p.create("inst-1", "p1", "v1", "A", ["E"])
        assert p.list_previews("inst-2") == []
