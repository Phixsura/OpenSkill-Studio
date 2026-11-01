from app.services.app_marketplace_app_app_app_app_app_app_app_event_source import EventStore

def test_append_read():
    es = EventStore()
    es.append("order-1", "created", {"amount": 100})
    es.append("order-1", "paid", {"method": "card"})
    events = es.read("order-1")
    assert len(events) == 2
    assert events[0]["version"] == 1
    assert events[1]["type"] == "paid"

def test_project():
    es = EventStore()
    es.append("cart-1", "item_added", {"item": "A", "qty": 2})
    es.append("cart-1", "item_added", {"item": "B", "qty": 1})
    es.append("cart-1", "item_removed", {"item": "A"})
    def reducer(state, event):
        items = dict(state.get("items", {}))
        if event["type"] == "item_added":
            items[event["data"]["item"]] = event["data"]["qty"]
        elif event["type"] == "item_removed":
            items.pop(event["data"]["item"], None)
        return {"items": items}
    result = es.project("cart-1", reducer)
    assert result["items"] == {"B": 1}
    assert es.stats()["total_events"] == 3
