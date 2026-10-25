from app.services.app_marketplace_extension_canary_deploy import (
    CanaryDeployService, CanaryState,
)


def test_create_and_start():
    cds = CanaryDeployService()
    d = cds.create("d1", "ext-1", "1.0.0", "2.0.0", step_percent=25)
    assert d.state == CanaryState.PENDING
    assert cds.start("d1") is True
    assert cds.get("d1").canary_percent == 25
    assert cds.get("d1").state == CanaryState.ROLLING_OUT


def test_advance_to_promotion():
    cds = CanaryDeployService()
    cds.create("d2", "ext-2", "1.0", "2.0", step_percent=50)
    cds.start("d2")
    ok, _ = cds.advance("d2")  # 50 -> 100
    assert ok
    assert cds.get("d2").state == CanaryState.PROMOTED


def test_auto_rollback_on_errors():
    cds = CanaryDeployService()
    cds.create("d3", "ext-3", "1.0", "2.0", error_threshold=5.0)
    cds.start("d3")
    # Simulate high error rate
    for _ in range(100):
        cds.record_request("d3", is_canary=True, is_error=False)
    for _ in range(10):
        cds.record_request("d3", is_canary=True, is_error=True)
    # Error rate: 10/110 ≈ 9.09% > 5%
    ok, msg = cds.advance("d3")
    assert ok is False
    assert "Auto-rollback" in msg
    assert cds.get("d3").state == CanaryState.ROLLED_BACK


def test_manual_rollback():
    cds = CanaryDeployService()
    cds.create("d4", "ext-4", "1.0", "2.0")
    cds.start("d4")
    assert cds.rollback("d4", "Looks bad") is True
    assert cds.get("d4").state == CanaryState.ROLLED_BACK
    assert cds.get("d4").canary_percent == 0


def test_routing():
    cds = CanaryDeployService()
    cds.create("d5", "ext-5", "1.0", "2.0", step_percent=30)
    cds.start("d5")
    routing = cds.get_routing("d5")
    assert routing["canary_percent"] == 30
    assert routing["stable_percent"] == 70


def test_steps_log():
    cds = CanaryDeployService()
    cds.create("d6", "ext-6", "1.0", "2.0", step_percent=50)
    cds.start("d6")
    cds.advance("d6")
    d = cds.get("d6")
    assert len(d.steps_log) >= 3  # start, advance, promoted
