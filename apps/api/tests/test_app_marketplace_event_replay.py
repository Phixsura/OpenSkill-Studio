from app.services.app_marketplace_event_replay import EventReplayService


def test_store_and_query():
    ers = EventReplayService()
    ers.store("e1", "install", "ext-1", {"org": "o1"})
    ers.store("e2", "review", "ext-1", {"rating": 5})
    ers.store("e3", "install", "ext-2", {"org": "o2"})
    results = ers.query(extension_id="ext-1")
    assert len(results) == 2


def test_query_by_type():
    ers = EventReplayService()
    ers.store("e1", "install", "ext-1", {})
    ers.store("e2", "review", "ext-1", {})
    results = ers.query(event_type="install")
    assert len(results) == 1


def test_replay():
    ers = EventReplayService()
    ers.store("e1", "install", "ext-1", {"org": "o1"})
    ers.store("e2", "review", "ext-1", {"rating": 5})
    results = ers.replay(["e1", "e2", "e999"])
    assert results[0]["status"] == "replayed"
    assert results[1]["status"] == "replayed"
    assert results[2]["status"] == "not_found"
    assert results[0]["replay_count"] == 1


def test_replay_twice():
    ers = EventReplayService()
    ers.store("e1", "install", "ext-1", {})
    ers.replay(["e1"])
    ers.replay(["e1"])
    events = ers.query(extension_id="ext-1")
    assert events[0].replay_count == 2


def test_retention():
    ers = EventReplayService(max_events=5)
    for i in range(10):
        ers.store(f"e{i}", "event", "ext", {})
    assert len(ers.query()) == 5


def test_replay_stats():
    ers = EventReplayService()
    ers.store("s1", "install", "ext-s", {})
    ers.store("s2", "review", "ext-s", {})
    ers.replay(["s1"])
    stats = ers.get_replay_stats("ext-s")
    assert stats["total_stored"] == 2
    assert stats["total_replayed"] == 1
    assert "install" in stats["event_types"]
