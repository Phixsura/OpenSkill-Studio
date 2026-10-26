from app.services.app_marketplace_onboarding_checklist import OnboardingChecklistService


def test_create_checklist():
    ocs = OnboardingChecklistService()
    steps = ocs.create_checklist("dev-1")
    assert len(steps) == 8
    assert all(not s.completed for s in steps)


def test_complete_step():
    ocs = OnboardingChecklistService()
    ocs.create_checklist("dev-2")
    ok, unlocks = ocs.complete_step("dev-2", "profile")
    assert ok is True
    assert "create_extension" in unlocks


def test_progress():
    ocs = OnboardingChecklistService()
    ocs.create_checklist("dev-3")
    ocs.complete_step("dev-3", "profile")
    ocs.complete_step("dev-3", "api_key")
    progress = ocs.get_progress("dev-3")
    assert progress["completed"] == 2
    assert progress["percent"] == 25.0
    assert progress["next_step"] == "first_ext"


def test_all_required_complete():
    ocs = OnboardingChecklistService()
    ocs.create_checklist("dev-4")
    for step in ["profile", "api_key", "first_ext", "add_tests", "security_scan"]:
        ocs.complete_step("dev-4", step)
    progress = ocs.get_progress("dev-4")
    assert progress["all_required_complete"] is True


def test_unlocked_capabilities():
    ocs = OnboardingChecklistService()
    ocs.create_checklist("dev-5")
    ocs.complete_step("dev-5", "profile")
    ocs.complete_step("dev-5", "api_key")
    caps = ocs.get_unlocked_capabilities("dev-5")
    assert "create_extension" in caps
    assert "api_access" in caps


def test_reset():
    ocs = OnboardingChecklistService()
    ocs.create_checklist("dev-6")
    ocs.complete_step("dev-6", "profile")
    ocs.reset("dev-6")
    progress = ocs.get_progress("dev-6")
    assert progress["completed"] == 0
