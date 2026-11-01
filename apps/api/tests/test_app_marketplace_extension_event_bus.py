from app.services.app_marketplace_extension_event_bus import ExtEventBusService

def test_pub_sub():
    svc = ExtEventBusService()
    svc.subscribe("ext-1", "install")
    svc.subscribe("ext-2", "install")
    evt = svc.publish("platform", "install", {"ext": "ext-3"})
    assert len(svc.get_subscribers("install")) == 2
    assert len(svc.get_events("install")) == 1

def test_unsubscribe():
    svc = ExtEventBusService()
    svc.subscribe("ext-1", "update")
    svc.unsubscribe("ext-1", "update")
    assert len(svc.get_subscribers("update")) == 0

def test_dead_letter():
    svc = ExtEventBusService()
    svc.publish("platform", "orphan-topic", {"data": 1})
    assert len(svc.get_dead_letters()) == 1

def test_topics():
    svc = ExtEventBusService()
    svc.subscribe("ext-1", "install")
    svc.subscribe("ext-1", "update")
    assert set(svc.get_topics()) == {"install", "update"}
