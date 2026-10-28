"""Tests for App API Changelog Reaction — react, unreact, counts."""

import pytest

from app.services.app_api_changelog_reaction import AppAPIChangelogReaction


class TestReact:
    def test_react(self):
        r = AppAPIChangelogReaction()
        entry = r.react("inst-1", "e1", "alice", "🚀")
        assert entry.total == 1

    def test_invalid_emoji(self):
        r = AppAPIChangelogReaction()
        with pytest.raises(ValueError):
            r.react("inst-1", "e1", "alice", "💀")

    def test_dedup(self):
        r = AppAPIChangelogReaction()
        r.react("inst-1", "e1", "alice", "🚀")
        r.react("inst-1", "e1", "alice", "🚀")
        assert r.get_reactions("inst-1", "e1").total == 1

    def test_multiple_emoji(self):
        r = AppAPIChangelogReaction()
        r.react("inst-1", "e1", "alice", "🚀")
        r.react("inst-1", "e1", "alice", "🎉")
        assert r.get_reactions("inst-1", "e1").total == 2


class TestUnreact:
    def test_unreact(self):
        r = AppAPIChangelogReaction()
        r.react("inst-1", "e1", "alice", "🚀")
        r.unreact("inst-1", "e1", "alice", "🚀")
        assert r.get_reactions("inst-1", "e1").total == 0


class TestIsolation:
    def test_cross(self):
        r = AppAPIChangelogReaction()
        r.react("inst-1", "e1", "alice", "👍")
        assert r.get_reactions("inst-2", "e1").total == 0
