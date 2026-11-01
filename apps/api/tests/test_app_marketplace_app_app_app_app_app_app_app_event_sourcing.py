from app.services.app_marketplace_app_app_app_app_app_app_app_event_sourcing import (
    append_event, get_events, project_state, store_stats, clear_events,
)

def test_event_sourcing():
    clear_events()
    append_event("user-1", "created", {"name": "Alice", "email": "alice@test.com"})
    append_event("user-1", "updated", {"name": "Alice Smith"})
    state = project_state("user-1")
    assert state["state"]["name"] == "Alice Smith"
    assert state["state"]["email"] == "alice@test.com"
    assert state["version"] == 2
    clear_events()

def test_stats():
    clear_events()
    append_event("a", "created", {})
    append_event("b", "created", {})
    append_event("a", "updated", {})
    s = store_stats()
    assert s["total_events"] == 3
    assert s["aggregates"] == 2
    assert s["by_type"]["created"] == 2
    clear_events()
