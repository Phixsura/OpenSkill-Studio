from app.services.app_api_changelog_archive import AppAPIChangelogArchive

class TestArchive:
    def test_add(self):
        a = AppAPIChangelogArchive()
        e = a.add_entry("inst-1", "e1", "Release v1", "v1")
        assert e.archived is False

    def test_archive(self):
        a = AppAPIChangelogArchive()
        a.add_entry("inst-1", "e1", "Old", "v1")
        a.archive("inst-1", "e1")
        assert len(a.active_entries("inst-1")) == 0
        assert len(a.archived_entries("inst-1")) == 1

    def test_mixed(self):
        a = AppAPIChangelogArchive()
        a.add_entry("inst-1", "e1", "Old", "v1")
        a.add_entry("inst-1", "e2", "New", "v2")
        a.archive("inst-1", "e1")
        assert len(a.active_entries("inst-1")) == 1

    def test_isolation(self):
        a = AppAPIChangelogArchive()
        a.add_entry("inst-1", "e1", "A", "v1")
        assert a.list_all("inst-2") == []
