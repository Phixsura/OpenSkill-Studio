from app.services.app_marketplace_extension_dev_onboarding import DevOnboardingService

def test_create_checklist():
    svc = DevOnboardingService()
    items = svc.get_or_create("u1")
    assert len(items) == 7

def test_complete_item():
    svc = DevOnboardingService()
    svc.get_or_create("u1")
    assert svc.complete_item("u1", "profile") is True
    assert svc.complete_item("u1", "profile") is False  # already done

def test_progress():
    svc = DevOnboardingService()
    svc.get_or_create("u1")
    svc.complete_item("u1", "profile")
    p = svc.get_progress("u1")
    assert p["completed"] == 1
    assert p["percentage"] == 14

def test_onboarded():
    svc = DevOnboardingService()
    svc.get_or_create("u1")
    assert svc.is_onboarded("u1") is False
    for iid in ["profile", "api_key", "extension"]:
        svc.complete_item("u1", iid)
    assert svc.is_onboarded("u1") is True
