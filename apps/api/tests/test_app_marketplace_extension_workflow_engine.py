from app.services.app_marketplace_extension_workflow_engine import WorkflowEngineService


def test_linear_workflow():
    eng = WorkflowEngineService()
    wf = eng.create("deploy")
    eng.add_step(wf.workflow_id, "build", "Build", lambda ctx: {"artifact": "app.zip"})
    eng.add_step(wf.workflow_id, "test", "Test", lambda ctx: {"passed": True}, depends_on=["build"])
    eng.add_step(wf.workflow_id, "deploy", "Deploy", lambda ctx: {"url": "https://app.com"}, depends_on=["test"])
    result = eng.execute(wf.workflow_id)
    assert result.status == "completed"
    assert result.context["url"] == "https://app.com"


def test_parallel_branches():
    eng = WorkflowEngineService()
    wf = eng.create("ci")
    eng.add_step(wf.workflow_id, "checkout", "Checkout", lambda ctx: {"code": True})
    eng.add_step(wf.workflow_id, "lint", "Lint", lambda ctx: {"lint_ok": True}, depends_on=["checkout"])
    eng.add_step(wf.workflow_id, "test", "Test", lambda ctx: {"test_ok": True}, depends_on=["checkout"])
    eng.add_step(wf.workflow_id, "build", "Build", lambda ctx: {"built": True}, depends_on=["checkout"])
    # Join: deploy depends on all three
    eng.add_step(wf.workflow_id, "deploy", "Deploy", lambda ctx: {"deployed": True},
                 depends_on=["lint", "test", "build"])
    result = eng.execute(wf.workflow_id)
    assert result.status == "completed"
    assert result.context["deployed"] is True


def test_conditional_skip():
    eng = WorkflowEngineService()
    wf = eng.create("release", {"is_hotfix": True})
    eng.add_step(wf.workflow_id, "test", "Test", lambda ctx: {})
    eng.add_step(wf.workflow_id, "full_qa", "Full QA", lambda ctx: {},
                 depends_on=["test"],
                 condition=lambda ctx: not ctx.get("is_hotfix"))
    eng.add_step(wf.workflow_id, "deploy", "Deploy", lambda ctx: {"done": True},
                 depends_on=["test"])
    result = eng.execute(wf.workflow_id)
    assert result.status == "completed"
    assert result.steps["full_qa"].status == "skipped"


def test_failure_stops_dependents():
    eng = WorkflowEngineService()
    wf = eng.create("fail-test")
    eng.add_step(wf.workflow_id, "step1", "OK", lambda ctx: {})
    eng.add_step(wf.workflow_id, "step2", "Fail",
                 lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")),
                 depends_on=["step1"])
    eng.add_step(wf.workflow_id, "step3", "Never", lambda ctx: {},
                 depends_on=["step2"])
    result = eng.execute(wf.workflow_id)
    assert result.status == "failed"
    assert result.steps["step3"].status == "pending"  # never reached


def test_retry():
    call_count = [0]
    def flaky(ctx):
        call_count[0] += 1
        if call_count[0] < 2:
            raise RuntimeError("transient")
        return {"ok": True}

    eng = WorkflowEngineService()
    wf = eng.create("retry-test")
    eng.add_step(wf.workflow_id, "flaky", "Flaky Step", flaky, max_retries=2)
    result = eng.execute(wf.workflow_id)
    assert result.status == "completed"
    assert call_count[0] == 2


def test_context_flows():
    eng = WorkflowEngineService()
    wf = eng.create("pipeline", {"input": "raw"})
    eng.add_step(wf.workflow_id, "transform",
                 "Transform", lambda ctx: {"data": ctx["input"].upper()})
    eng.add_step(wf.workflow_id, "validate",
                 "Validate", lambda ctx: {"valid": ctx["data"] == "RAW"},
                 depends_on=["transform"])
    result = eng.execute(wf.workflow_id)
    assert result.context["valid"] is True


def test_status():
    eng = WorkflowEngineService()
    wf = eng.create("status-test")
    eng.add_step(wf.workflow_id, "a", "A", lambda ctx: {})
    eng.add_step(wf.workflow_id, "b", "B", lambda ctx: {}, depends_on=["a"])
    eng.execute(wf.workflow_id)
    status = eng.get_status(wf.workflow_id)
    assert status["progress"] == "2/2"
