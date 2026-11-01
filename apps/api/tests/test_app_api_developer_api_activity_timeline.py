from app.services.app_api_developer_api_activity_timeline import AppAPIDeveloperAPIActivityTimeline

class TestTimeline:
    def test_record(self):
        t = AppAPIDeveloperAPIActivityTimeline()
        e = t.record("inst-1", "e1", "alice", "created", "API Key k1")
        assert e.actor == "alice"

    def test_recent(self):
        t = AppAPIDeveloperAPIActivityTimeline()
        for i in range(5): t.record("inst-1", f"e{i}", "alice", "action", f"resource-{i}")
        r = t.recent("inst-1", 3)
        assert len(r) == 3
        assert r[0].event_id == "e4"

    def test_by_actor(self):
        t = AppAPIDeveloperAPIActivityTimeline()
        t.record("inst-1", "e1", "alice", "create", "app")
        t.record("inst-1", "e2", "bob", "delete", "key")
        assert len(t.by_actor("inst-1", "alice")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIActivityTimeline()
        t.record("inst-1", "e1", "alice", "action", "resource")
        assert t.count("inst-2") == 0
