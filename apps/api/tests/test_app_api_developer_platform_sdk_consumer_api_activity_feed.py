"""Tests for Consumer Activity Feed service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_activity_feed import (
    ActivityFeed, Activity,
)


class TestActivityFeed:
    def _act(self, aid, cid="c1", atype="api_call", actor="u1", desc="test"):
        return Activity(aid, cid, atype, actor, desc)

    def test_post_and_get(self):
        svc = ActivityFeed()
        svc.post(self._act("a1"))
        svc.post(self._act("a2"))
        feed = svc.get_feed()
        assert len(feed) == 2
        assert feed[0]["activity_id"] == "a2"  # reverse chrono

    def test_filter_by_consumer(self):
        svc = ActivityFeed()
        svc.post(self._act("a1", cid="c1"))
        svc.post(self._act("a2", cid="c2"))
        feed = svc.get_feed(consumer_id="c1")
        assert len(feed) == 1

    def test_filter_by_type(self):
        svc = ActivityFeed()
        svc.post(self._act("a1", atype="api_call"))
        svc.post(self._act("a2", atype="key_created"))
        feed = svc.get_feed(activity_type="key_created")
        assert len(feed) == 1

    def test_unread_filter(self):
        svc = ActivityFeed()
        svc.post(self._act("a1"))
        svc.post(self._act("a2"))
        svc.mark_read("a1")
        feed = svc.get_feed(unread_only=True)
        assert len(feed) == 1

    def test_mark_all_read(self):
        svc = ActivityFeed()
        svc.post(self._act("a1", cid="c1"))
        svc.post(self._act("a2", cid="c1"))
        svc.post(self._act("a3", cid="c2"))
        result = svc.mark_all_read("c1")
        assert result["marked"] == 2
        assert svc.get_unread_count("c1")["unread"] == 0

    def test_unread_count(self):
        svc = ActivityFeed()
        svc.post(self._act("a1", cid="c1"))
        svc.post(self._act("a2", cid="c1"))
        assert svc.get_unread_count("c1")["unread"] == 2

    def test_pagination(self):
        svc = ActivityFeed()
        for i in range(10):
            svc.post(self._act(f"a{i}"))
        page1 = svc.get_feed(limit=3, offset=0)
        page2 = svc.get_feed(limit=3, offset=3)
        assert len(page1) == 3
        assert len(page2) == 3
        assert page1[0]["activity_id"] != page2[0]["activity_id"]

    def test_stats(self):
        svc = ActivityFeed()
        svc.post(self._act("a1", atype="api_call"))
        svc.post(self._act("a2", atype="api_call"))
        svc.post(self._act("a3", atype="key_created"))
        stats = svc.get_stats()
        assert stats["total"] == 3
        assert stats["by_type"]["api_call"] == 2

    def test_invalid_type(self):
        svc = ActivityFeed()
        with pytest.raises(ValueError):
            svc.post(Activity("a1", "c1", "invalid_type", "u1", "bad"))

    def test_isolation(self):
        a, b = ActivityFeed(), ActivityFeed()
        a.post(self._act("a1"))
        assert b.get_feed() == []
