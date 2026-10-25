from app.services.app_marketplace_extension_lifecycle import (
    ExtensionLifecycle, LifecycleState,
)


def test_create_and_state():
    lc = ExtensionLifecycle()
    ext = lc.create("ext-1", "My Extension", "dev-1")
    assert ext["state"] == LifecycleState.DRAFT
    assert lc.get_state("ext-1") == LifecycleState.DRAFT


def test_full_happy_path():
    lc = ExtensionLifecycle()
    lc.create("ext-2", "Good Plugin", "dev-2")
    ok, _ = lc.submit("ext-2", "dev-2")
    assert ok
    ok, _ = lc.approve("ext-2", "reviewer-1", "Looks good")
    assert ok
    ok, _ = lc.publish("ext-2", "dev-2")
    assert ok
    assert lc.get_state("ext-2") == LifecycleState.PUBLISHED


def test_invalid_transition():
    lc = ExtensionLifecycle()
    lc.create("ext-3", "Bad Path", "dev-3")
    ok, msg = lc.transition("ext-3", LifecycleState.PUBLISHED, "dev-3")
    assert ok is False
    assert "Cannot transition" in msg


def test_reject_and_resubmit():
    lc = ExtensionLifecycle()
    lc.create("ext-4", "Fixable", "dev-4")
    lc.submit("ext-4", "dev-4")
    ok, _ = lc.reject("ext-4", "reviewer-2", "Needs fixes")
    assert ok
    assert lc.get_state("ext-4") == LifecycleState.REJECTED
    # Can go back to draft
    ok2, _ = lc.transition("ext-4", LifecycleState.DRAFT, "dev-4")
    assert ok2


def test_audit_log():
    lc = ExtensionLifecycle()
    lc.create("ext-5", "Audited", "dev-5")
    lc.submit("ext-5", "dev-5")
    log = lc.get_audit_log("ext-5")
    assert len(log) == 2
    assert log[0]["action"] == "created"
    assert "submitted" in log[1]["state"]


def test_list_by_state():
    lc = ExtensionLifecycle()
    lc.create("ext-a", "A", "dev")
    lc.create("ext-b", "B", "dev")
    lc.submit("ext-a", "dev")
    drafts = lc.list_by_state(LifecycleState.DRAFT)
    submitted = lc.list_by_state(LifecycleState.SUBMITTED)
    assert any(e["extension_id"] == "ext-b" for e in drafts)
    assert any(e["extension_id"] == "ext-a" for e in submitted)


def test_suspend_published():
    lc = ExtensionLifecycle()
    lc.create("ext-s", "Suspendable", "dev")
    lc.submit("ext-s", "dev")
    lc.approve("ext-s", "rev")
    lc.publish("ext-s", "dev")
    ok, _ = lc.transition("ext-s", LifecycleState.SUSPENDED, "admin", "Policy violation")
    assert ok
    assert lc.get_state("ext-s") == LifecycleState.SUSPENDED
