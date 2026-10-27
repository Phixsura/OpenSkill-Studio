from app.services.app_marketplace_extension_welcome_flow import ExtWelcomeFlowService

def test_start():
    svc = ExtWelcomeFlowService()
    steps = svc.start("u1")
    assert len(steps) == 5

def test_complete():
    svc = ExtWelcomeFlowService()
    svc.start("u1")
    svc.complete_step("u1", "explore")
    p = svc.get_progress("u1")
    assert p["completed"] == 1
    assert p["percentage"] == 20

def test_skip():
    svc = ExtWelcomeFlowService()
    svc.start("u1")
    svc.skip("u1")
    assert svc.get_progress("u1")["all_done"] is True
