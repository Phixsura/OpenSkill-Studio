from app.services.app_marketplace_extension_welcome import ExtensionWelcomeService


def test_new_developer():
    svc = ExtensionWelcomeService()
    data = svc.generate("dev-1", "Alice")
    assert "Create your first extension" in data.suggested_actions
    greeting = svc.get_greeting("dev-1")
    assert "first extension" in greeting


def test_active_developer():
    svc = ExtensionWelcomeService()
    data = svc.generate("dev-1", "Bob", extensions=5, installs=500, onboarding_done=True)
    assert "verified developer" in data.suggested_actions[0].lower()
    greeting = svc.get_greeting("dev-1")
    assert "500" in greeting


def test_onboarding_incomplete():
    svc = ExtensionWelcomeService()
    data = svc.generate("dev-1", "Charlie", onboarding_done=False)
    assert any("getting started" in a.lower() for a in data.suggested_actions)


def test_unknown_developer():
    svc = ExtensionWelcomeService()
    greeting = svc.get_greeting("unknown")
    assert "Welcome to" in greeting
