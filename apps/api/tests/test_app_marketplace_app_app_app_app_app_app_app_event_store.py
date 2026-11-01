from app.services.app_marketplace_app_app_app_app_app_app_app_event_store import EventStore

def test_event_store():
    store = EventStore()
    store.append("order-1", event_type="created", data={"total": 100})
    store.append("order-1", event_type="paid", data={"method": "card"})
    store.append("order-1", event_type="shipped", data={"tracking": "TRK123"})
    events = store.read_stream("order-1")
    assert len(events) == 3
    assert events[0]["type"] == "created"
    after = store.read_stream("order-1", after_seq=1)
    assert len(after) == 2

    def reducer(state, event):
        state["status"] = event["type"]
        state.update(event["data"])
        return state

    proj = store.project("order-1", reducer, {"status": "unknown"})
    assert proj["state"]["status"] == "shipped"
    assert proj["state"]["tracking"] == "TRK123"
    assert proj["version"] == 3
    assert store.stats()["total_events"] == 3
