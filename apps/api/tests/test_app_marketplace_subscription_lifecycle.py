from app.services.app_marketplace_subscription_lifecycle import (
    SubscriptionLifecycleService, SubState,
)


def test_create_active():
    sls = SubscriptionLifecycleService()
    sub = sls.create("s1", "org-1", "ext-1", "plan-pro", 999)
    assert sub.state == SubState.ACTIVE


def test_create_trial():
    sls = SubscriptionLifecycleService()
    sub = sls.create("s2", "org-1", "ext-1", "plan-pro", 999, trial=True)
    assert sub.state == SubState.TRIAL


def test_cancel():
    sls = SubscriptionLifecycleService()
    sls.create("s3", "org-1", "ext-1", "plan", 500)
    ok, _ = sls.transition("s3", SubState.CANCELED, "User requested")
    assert ok
    assert sls.get("s3").cancel_reason == "User requested"


def test_invalid_transition():
    sls = SubscriptionLifecycleService()
    sls.create("s4", "org-1", "ext-1", "plan", 500)
    ok, msg = sls.transition("s4", SubState.EXPIRED)
    assert ok is False
    assert "Cannot transition" in msg


def test_dunning_flow():
    sls = SubscriptionLifecycleService(max_dunning_attempts=2)
    sls.create("s5", "org-1", "ext-1", "plan", 999)
    sls.record_payment_failure("s5")
    assert sls.get("s5").state == SubState.PAST_DUE
    sls.record_payment_failure("s5")
    assert sls.get("s5").state == SubState.GRACE_PERIOD


def test_payment_recovery():
    sls = SubscriptionLifecycleService()
    sls.create("s6", "org-1", "ext-1", "plan", 999)
    sls.transition("s6", SubState.PAST_DUE, "fail")
    assert sls.record_payment_success("s6") is True
    assert sls.get("s6").state == SubState.ACTIVE
    assert sls.get("s6").dunning_attempts == 0


def test_state_history():
    sls = SubscriptionLifecycleService()
    sls.create("s7", "org-1", "ext-1", "plan", 500)
    sls.transition("s7", SubState.CANCELED, "done")
    history = sls.get("s7").state_history
    assert len(history) == 2
    assert history[0]["state"] == "active"
    assert history[1]["state"] == "canceled"


def test_mrr():
    sls = SubscriptionLifecycleService()
    sls.create("m1", "org-1", "ext-1", "p1", 999)
    sls.create("m2", "org-2", "ext-2", "p2", 1999)
    sls.create("m3", "org-3", "ext-3", "p3", 500)
    sls.transition("m3", SubState.CANCELED)
    assert sls.get_mrr() == 2998  # m1 + m2, not m3
