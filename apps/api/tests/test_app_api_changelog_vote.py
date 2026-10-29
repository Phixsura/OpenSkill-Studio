from app.services.app_api_changelog_vote import AppAPIChangelogVote

class TestVote:
    def test_upvote(self):
        v = AppAPIChangelogVote()
        ev = v.upvote("inst-1", "e1", "alice")
        assert ev.score == 1

    def test_switch_vote(self):
        v = AppAPIChangelogVote()
        v.upvote("inst-1", "e1", "alice")
        ev = v.downvote("inst-1", "e1", "alice")
        assert ev.score == -1
        assert "alice" not in ev.upvotes

    def test_top(self):
        v = AppAPIChangelogVote()
        v.upvote("inst-1", "e1", "a")
        v.upvote("inst-1", "e1", "b")
        v.upvote("inst-1", "e2", "a")
        top = v.top_entries("inst-1")
        assert top[0].entry_id == "e1"

    def test_isolation(self):
        v = AppAPIChangelogVote()
        v.upvote("inst-1", "e1", "a")
        assert v.top_entries("inst-2") == []
