import pytest
from app.services.app_api_changelog_roadmap import AppAPIChangelogRoadmap, RoadmapStatus

class TestRoadmap:
    def test_add(self):
        r = AppAPIChangelogRoadmap()
        item = r.add_item("inst-1", "i1", "Dark Mode", "Add dark theme", "v3.0")
        assert item.status == RoadmapStatus.PLANNED

    def test_lifecycle(self):
        r = AppAPIChangelogRoadmap()
        r.add_item("inst-1", "i1", "Feature", "Desc", "v3.0")
        r.update_status("inst-1", "i1", RoadmapStatus.IN_PROGRESS)
        r.update_status("inst-1", "i1", RoadmapStatus.COMPLETED)
        assert r.by_status("inst-1", RoadmapStatus.COMPLETED)[0].item_id == "i1"

    def test_vote(self):
        r = AppAPIChangelogRoadmap()
        r.add_item("inst-1", "i1", "F", "D", "v3")
        r.vote("inst-1", "i1")
        r.vote("inst-1", "i1")
        assert r.list_items("inst-1")[0].vote_count == 2

    def test_isolation(self):
        r = AppAPIChangelogRoadmap()
        r.add_item("inst-1", "i1", "F", "D", "v3")
        assert r.list_items("inst-2") == []
