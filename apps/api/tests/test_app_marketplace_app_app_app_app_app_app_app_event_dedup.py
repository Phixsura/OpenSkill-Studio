from app.services.app_marketplace_app_app_app_app_app_app_app_event_dedup import EventDedup

def test_dedup():
    ed = EventDedup()
    r1 = ed.check("evt-1")
    assert not r1["duplicate"]
    r2 = ed.check("evt-1")
    assert r2["duplicate"]
    r3 = ed.check("evt-2")
    assert not r3["duplicate"]
    assert ed.stats()["deduped"] == 1
