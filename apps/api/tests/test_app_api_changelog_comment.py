"""Tests for App API Changelog Comment — add, thread, hide."""

import pytest
from app.services.app_api_changelog_comment import AppAPIChangelogComment


class TestComment:
    def test_add(self):
        c = AppAPIChangelogComment()
        cm = c.add_comment("inst-1", "c1", "e1", "alice", "Great update!")
        assert cm.parent_id is None

    def test_empty_body(self):
        c = AppAPIChangelogComment()
        with pytest.raises(ValueError, match="empty"):
            c.add_comment("inst-1", "c1", "e1", "alice", "  ")


class TestThread:
    def test_reply(self):
        c = AppAPIChangelogComment()
        c.add_comment("inst-1", "c1", "e1", "alice", "Nice!")
        c.add_comment("inst-1", "c2", "e1", "bob", "Thanks!", parent_id="c1")
        assert len(c.replies("inst-1", "c1")) == 1


class TestModeration:
    def test_hide(self):
        c = AppAPIChangelogComment()
        c.add_comment("inst-1", "c1", "e1", "alice", "Spam")
        c.hide_comment("inst-1", "c1")
        assert c.count("inst-1", "e1") == 0


class TestIsolation:
    def test_cross(self):
        c = AppAPIChangelogComment()
        c.add_comment("inst-1", "c1", "e1", "alice", "Hi")
        assert c.count("inst-2", "e1") == 0
