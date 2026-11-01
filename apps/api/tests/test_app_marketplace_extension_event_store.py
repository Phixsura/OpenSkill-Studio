from app.services.app_marketplace_extension_event_store import EventStoreService


def test_append_and_get():
    store = EventStoreService()
    e1 = store.append("order-1", "created", {"total": 100})
    e2 = store.append("order-1", "item_added", {"item": "widget"})
    events = store.get_events("order-1")
    assert len(events) == 2
    assert events[0].version == 1
    assert events[1].version == 2


def test_optimistic_concurrency():
    store = EventStoreService()
    store.append("order-1", "created", {}, expected_version=0)
    # Concurrent write with stale version should fail
    store.append("order-1", "updated", {}, expected_version=1)
    try:
        store.append("order-1", "conflict", {}, expected_version=1)
        assert False
    except ValueError as e:
        assert "Concurrency conflict" in str(e)


def test_event_type_filter():
    store = EventStoreService()
    store.append("a-1", "created", {})
    store.append("a-1", "updated", {})
    store.append("a-1", "updated", {})
    store.append("a-1", "deleted", {})
    updates = store.get_events("a-1", event_type="updated")
    assert len(updates) == 2


def test_after_version():
    store = EventStoreService()
    for i in range(5):
        store.append("a-1", "event", {"i": i})
    events = store.get_events("a-1", after_version=3)
    assert len(events) == 2
    assert events[0].version == 4


def test_snapshot_and_rebuild():
    store = EventStoreService()
    store.append("cart-1", "item_added", {"item": "A", "qty": 1})
    store.append("cart-1", "item_added", {"item": "B", "qty": 2})

    # Save snapshot at current state
    store.save_snapshot("cart-1", {"items": {"A": 1, "B": 2}, "total": 3})

    # Add more events after snapshot
    store.append("cart-1", "item_removed", {"item": "A"})

    def reducer(state, event):
        if not state.get("items"):
            state["items"] = {}
            state["total"] = 0
        if event.event_type == "item_added":
            state["items"][event.data["item"]] = event.data["qty"]
            state["total"] += event.data["qty"]
        elif event.event_type == "item_removed":
            qty = state["items"].pop(event.data["item"], 0)
            state["total"] -= qty
        return state

    rebuilt = store.rebuild("cart-1", reducer)
    assert rebuilt["items"] == {"B": 2}
    assert rebuilt["total"] == 2


def test_rebuild_without_snapshot():
    store = EventStoreService()
    store.append("counter", "increment", {"amount": 5})
    store.append("counter", "increment", {"amount": 3})
    store.append("counter", "decrement", {"amount": 2})

    def reducer(state, event):
        if "value" not in state:
            state["value"] = 0
        if event.event_type == "increment":
            state["value"] += event.data["amount"]
        elif event.event_type == "decrement":
            state["value"] -= event.data["amount"]
        return state

    result = store.rebuild("counter", reducer)
    assert result["value"] == 6


def test_version():
    store = EventStoreService()
    assert store.get_version("new") == 0
    store.append("new", "created", {})
    assert store.get_version("new") == 1


def test_aggregate_ids():
    store = EventStoreService()
    store.append("a", "created", {})
    store.append("b", "created", {})
    assert set(store.get_all_aggregate_ids()) == {"a", "b"}
