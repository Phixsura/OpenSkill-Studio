from app.services.app_marketplace_extension_saga_orchestrator import (
    SagaOrchestratorService, SagaState, StepState
)


def test_successful_saga():
    svc = SagaOrchestratorService()
    saga = svc.create("order", {"order_id": "o1"})
    svc.add_step(saga.saga_id, "reserve_inventory",
                 lambda ctx: {"reserved": True},
                 lambda ctx: None)
    svc.add_step(saga.saga_id, "charge_payment",
                 lambda ctx: {"payment_id": "pay-1"},
                 lambda ctx: None)
    svc.add_step(saga.saga_id, "send_confirmation",
                 lambda ctx: {"email_sent": True},
                 lambda ctx: None)
    result = svc.execute(saga.saga_id)
    assert result.state == SagaState.COMPLETED
    assert all(s.state == StepState.COMPLETED for s in result.steps)
    assert result.context["payment_id"] == "pay-1"


def test_failure_triggers_compensation():
    svc = SagaOrchestratorService()
    compensated = []
    saga = svc.create("order")
    svc.add_step(saga.saga_id, "step1",
                 lambda ctx: {"done": 1},
                 lambda ctx: compensated.append("step1"))
    svc.add_step(saga.saga_id, "step2",
                 lambda ctx: {"done": 2},
                 lambda ctx: compensated.append("step2"))
    svc.add_step(saga.saga_id, "step3_fail",
                 lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")),
                 lambda ctx: compensated.append("step3"))
    result = svc.execute(saga.saga_id)
    assert result.state == SagaState.COMPENSATED
    # Step 1 and 2 should be compensated in reverse order
    assert compensated == ["step2", "step1"]
    # Step 3 should be failed, not compensated
    assert result.steps[2].state == StepState.FAILED


def test_remaining_steps_skipped():
    svc = SagaOrchestratorService()
    saga = svc.create("test")
    svc.add_step(saga.saga_id, "ok",
                 lambda ctx: {}, lambda ctx: None)
    svc.add_step(saga.saga_id, "fail",
                 lambda ctx: (_ for _ in ()).throw(ValueError("err")),
                 lambda ctx: None)
    svc.add_step(saga.saga_id, "never_runs",
                 lambda ctx: {}, lambda ctx: None)
    result = svc.execute(saga.saga_id)
    assert result.steps[2].state == StepState.SKIPPED


def test_compensation_failure():
    svc = SagaOrchestratorService()
    saga = svc.create("risky")
    svc.add_step(saga.saga_id, "step1",
                 lambda ctx: {},
                 lambda ctx: (_ for _ in ()).throw(RuntimeError("comp failed")))
    svc.add_step(saga.saga_id, "step2_fail",
                 lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")),
                 lambda ctx: None)
    result = svc.execute(saga.saga_id)
    assert result.state == SagaState.FAILED  # compensation failed


def test_context_flows_between_steps():
    svc = SagaOrchestratorService()
    saga = svc.create("pipeline", {"input": "data"})
    svc.add_step(saga.saga_id, "transform",
                 lambda ctx: {"transformed": ctx["input"].upper()},
                 lambda ctx: None)
    svc.add_step(saga.saga_id, "validate",
                 lambda ctx: {"valid": ctx["transformed"] == "DATA"},
                 lambda ctx: None)
    result = svc.execute(saga.saga_id)
    assert result.context["valid"] is True


def test_status():
    svc = SagaOrchestratorService()
    saga = svc.create("status_test")
    svc.add_step(saga.saga_id, "a", lambda ctx: {}, lambda ctx: None)
    svc.add_step(saga.saga_id, "b", lambda ctx: {}, lambda ctx: None)
    svc.execute(saga.saga_id)
    status = svc.get_status(saga.saga_id)
    assert status["state"] == "completed"
    assert status["completed"] == 2
    assert status["total"] == 2
