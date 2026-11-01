"""Tests for App Changelog Mention — extract, index, query."""

import pytest

from app.services.app_changelog_mention import AppChangelogMention


TEXT_V1 = """
## v1.0.0

- Added user authentication (@alice, @bob)
- Fixed #42 — login redirect bug
- Merged PR #10 with new dashboard
"""

TEXT_V2 = """
## v2.0.0

- Performance improvements by @alice
- Resolved #42 and #55
- PR-15: API rate limiting
"""


class TestExtract:
    def test_extract_users(self):
        m = AppChangelogMention()
        idx = m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        assert idx.users == ["alice", "bob"]

    def test_extract_issues(self):
        m = AppChangelogMention()
        idx = m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        assert idx.issues == [42]

    def test_extract_prs(self):
        m = AppChangelogMention()
        idx = m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        assert idx.prs == [10]

    def test_dedup(self):
        m = AppChangelogMention()
        idx = m.extract_and_index("inst-1", "2.0.0", TEXT_V2)
        assert idx.issues == [42, 55]

    def test_pr_formats(self):
        m = AppChangelogMention()
        idx = m.extract_and_index("inst-1", "2.0.0", TEXT_V2)
        assert 15 in idx.prs

    def test_missing_version(self):
        m = AppChangelogMention()
        with pytest.raises(ValueError, match="version"):
            m.extract_and_index("inst-1", "", "text")


class TestQuery:
    def test_find_by_user(self):
        m = AppChangelogMention()
        m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        m.extract_and_index("inst-1", "2.0.0", TEXT_V2)
        versions = m.find_by_user("inst-1", "alice")
        assert versions == ["1.0.0", "2.0.0"]

    def test_find_by_issue(self):
        m = AppChangelogMention()
        m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        m.extract_and_index("inst-1", "2.0.0", TEXT_V2)
        versions = m.find_by_issue("inst-1", 42)
        assert versions == ["1.0.0", "2.0.0"]

    def test_find_by_pr(self):
        m = AppChangelogMention()
        m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        versions = m.find_by_pr("inst-1", 10)
        assert versions == ["1.0.0"]

    def test_all_mentioned_users(self):
        m = AppChangelogMention()
        m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        m.extract_and_index("inst-1", "2.0.0", TEXT_V2)
        assert m.all_mentioned_users("inst-1") == ["alice", "bob"]


class TestIsolation:
    def test_cross_installation(self):
        m = AppChangelogMention()
        m.extract_and_index("inst-1", "1.0.0", TEXT_V1)
        assert m.find_by_user("inst-2", "alice") == []
