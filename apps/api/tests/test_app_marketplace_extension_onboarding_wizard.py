from app.services.app_marketplace_extension_onboarding_wizard import (
    ExtensionOnboardingWizardService,
)


def test_start():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    assert len(session.steps) == 6
    assert session.current_step == 0


def test_complete_step():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    result = svc.complete_step(session.session_id, {"name": "My Ext"})
    assert result["ok"] is True
    assert session.current_step == 1


def test_skip_optional():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    # Advance to branding (index 3, optional)
    for _ in range(3):
        svc.complete_step(session.session_id)
    result = svc.skip_step(session.session_id)
    assert result["ok"] is True


def test_cannot_skip_required():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    result = svc.skip_step(session.session_id)  # first step is required
    assert result["ok"] is False


def test_go_back():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    svc.complete_step(session.session_id)
    assert svc.go_back(session.session_id) is True
    assert session.current_step == 0


def test_progress():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    svc.complete_step(session.session_id)
    svc.complete_step(session.session_id)
    progress = svc.get_progress(session.session_id)
    assert progress["completed"] == 2
    assert progress["percent"] == 33


def test_full_completion():
    svc = ExtensionOnboardingWizardService()
    session = svc.start("ext-1", "dev-1")
    for i in range(6):
        if i == 3:  # branding is optional
            svc.skip_step(session.session_id)
        else:
            svc.complete_step(session.session_id)
    assert session.completed is True
