from app.services.app_marketplace_app_app_app_app_app_app_app_es_projector import EventProjector

def test_project():
    ep = EventProjector()
    ep.register_projection("order_count", {"count": 0})
    def reducer(state, event):
        if event["type"] == "order.created":
            return {"count": state["count"] + 1}
        return state
    ep.apply("order_count", {"type": "order.created"}, reducer)
    ep.apply("order_count", {"type": "order.created"}, reducer)
    ep.apply("order_count", {"type": "other"}, reducer)
    assert ep.get_state("order_count")["count"] == 2
    assert ep.stats()["total_events"] == 3
