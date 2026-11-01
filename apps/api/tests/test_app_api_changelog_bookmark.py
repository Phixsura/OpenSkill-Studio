from app.services.app_api_changelog_bookmark import AppAPIChangelogBookmark

class TestBookmark:
    def test_add(self):
        b = AppAPIChangelogBookmark()
        bm = b.add("inst-1", "alice", "e1", "Important update")
        assert bm.note == "Important update"

    def test_remove(self):
        b = AppAPIChangelogBookmark()
        b.add("inst-1", "alice", "e1")
        b.remove("inst-1", "alice", "e1")
        assert not b.is_bookmarked("inst-1", "alice", "e1")

    def test_list(self):
        b = AppAPIChangelogBookmark()
        b.add("inst-1", "alice", "e1")
        b.add("inst-1", "alice", "e2")
        b.add("inst-1", "bob", "e1")
        assert len(b.list_bookmarks("inst-1", "alice")) == 2

    def test_isolation(self):
        b = AppAPIChangelogBookmark()
        b.add("inst-1", "alice", "e1")
        assert b.list_bookmarks("inst-2", "alice") == []
