from app.services.app_marketplace_app_app_app_app_app_app_app_event_replay import EventReplayEngine

def test_replay():
    er = EventReplayEngine()
    er.store("order.created", {"id": "o1"}, 100)
    er.store("order.paid", {"id": "o1"}, 101)
    er.store("user.signup", {"id": "u1"}, 102)
    r = er.replay(from_seq=2)
    assert r["count"] == 2
    r2 = er.replay(event_type="order.created")
    assert r2["count"] == 1

def test_range():
    er = EventReplayEngine()
    for i in range(10):
        er.store("tick", {"i": i}, i)
    r = er.replay(from_seq=3, to_seq=7)
    assert r["count"] == 5
    assert er.stats()["total_events"] == 10
