import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_community_forum import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum

class TestCommunityForum:
    def test_create(self):
        f = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum()
        p = f.create_post("inst-1", "p1", "dev1", "How to auth?", "question")
        assert p.status == "open"

    def test_reply_and_upvote(self):
        f = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum()
        f.create_post("inst-1", "p1", "dev1", "Question", "question")
        f.reply("inst-1", "p1")
        f.upvote("inst-1", "p1")
        p = f.trending("inst-1")[0]
        assert p.reply_count == 1
        assert p.upvotes == 1

    def test_unanswered(self):
        f = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum()
        f.create_post("inst-1", "p1", "d1", "Q1", "question")
        f.create_post("inst-1", "p2", "d2", "Q2", "question")
        f.mark_answered("inst-1", "p1")
        assert len(f.unanswered("inst-1")) == 1

    def test_by_category(self):
        f = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum()
        f.create_post("inst-1", "p1", "d1", "Q", "question")
        f.create_post("inst-1", "p2", "d2", "D", "discussion")
        assert f.by_category("inst-1") == {"question": 1, "discussion": 1}

    def test_isolation(self):
        f = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperCommunityForum()
        f.create_post("inst-1", "p1", "d1", "X", "question")
        assert len(f.trending("inst-2")) == 0
