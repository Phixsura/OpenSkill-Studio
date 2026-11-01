from app.services.app_marketplace_extension_automation_trigger_registry import AutomationTriggerRegistryService

def test_register_and_fire():
    svc = AutomationTriggerRegistryService()
    t = svc.register("Daily Sync", "schedule", {"cron": "0 0 * * *"}, "u1")
    result = svc.fire(t.trigger_id)
    assert result["fire_count"] == 1

def test_toggle():
    svc = AutomationTriggerRegistryService()
    t = svc.register("Hook", "webhook", {}, "u1")
    svc.toggle(t.trigger_id, False)
    assert svc.fire(t.trigger_id) is None

def test_list_by_type():
    svc = AutomationTriggerRegistryService()
    svc.register("A", "schedule", {}, "u1")
    svc.register("B", "webhook", {}, "u1")
    svc.register("C", "schedule", {}, "u1")
    assert len(svc.list_by_type("schedule")) == 2

def test_delete():
    svc = AutomationTriggerRegistryService()
    t = svc.register("X", "manual", {}, "u1")
    assert svc.delete(t.trigger_id) is True
    assert len(svc.list_all()) == 0
