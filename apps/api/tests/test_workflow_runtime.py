"""Tests for the workflow execution runtime (ADR-010 D6).

Covers: run creation + idempotency, step advancement, review gates
(suspend → decide → resume, 409 on double-decide, reject → FAILED + SKIPPED),
cancellation, mock provider execution, output caps, capability gates.
"""

import asyncio
import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def c():
    from app.core.database import engine
    from app.main import app
    from app.services.workflow_runtime import drain_workflow_tasks

    orig = app.router.lifespan_context

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    await drain_workflow_tasks()
    app.router.lifespan_context = orig
    await engine.dispose()


def _email():
    return f"wfr-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "WFR"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"R-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


def _definition(with_review=False, with_provider=False):
    """Text-only pipeline: asset_input(text) → prompt_template → [provider] → [review] → output."""
    steps = [
        {
            "id": "take_input",
            "type": "asset_input",
            "name": "Take input",
            "config": {"accept_types": ["image"]},
            "inputs": [],
            "outputs": [{"port": "topic", "type": "text"}],
        },
        {
            "id": "build_prompt",
            "type": "prompt_template",
            "name": "Build prompt",
            "config": {"template": "Write about {{inputs.topic}}"},
            "inputs": [{"port": "topic", "type": "text"}],
            "outputs": [{"port": "prompt", "type": "prompt"}],
        },
    ]
    edges = [
        {"id": "e1", "from_step": "take_input", "from_port": "topic", "to_step": "build_prompt", "to_port": "topic"},
    ]
    last_step, last_port, last_type = "build_prompt", "prompt", "prompt"

    if with_provider:
        steps.append(
            {
                "id": "generate",
                "type": "provider_action",
                "name": "Generate",
                "config": {"capability": "image_generation"},
                "inputs": [{"port": "prompt", "type": "prompt"}],
                "outputs": [{"port": "result", "type": "image"}],
            }
        )
        edges.append(
            {"id": "e2", "from_step": last_step, "from_port": last_port, "to_step": "generate", "to_port": "prompt"}
        )
        last_step, last_port, last_type = "generate", "result", "image"

    if with_review:
        steps.append(
            {
                "id": "qa",
                "type": "review_gate",
                "name": "QA",
                "config": {"instructions": "Check quality", "due_days": 7},
                "inputs": [{"port": "subject", "type": last_type}],
                "outputs": [
                    {"port": "decision", "type": "selection"},
                    {"port": "passed", "type": last_type},
                ],
            }
        )
        edges.append(
            {"id": "e3", "from_step": last_step, "from_port": last_port, "to_step": "qa", "to_port": "subject"}
        )
        last_step, last_port = "qa", "passed"

    return {
        "schema_version": 1,
        "inputs": [{"key": "topic", "type": "text", "required": True}],
        "outputs": [{"key": "final", "type": last_type, "from_step": last_step, "from_port": last_port}],
        "steps": steps,
        "edges": edges,
        "ui": {},
    }


async def _install(c, h, oid, definition):
    """Create pack, set definition, publish, install into same org."""
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": f"RT-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": definition},
        headers=h,
    )
    assert r2.status_code == 200, r2.text
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r3.status_code == 201, r3.text
    release_id = r3.json()["data"]["id"]

    # Direct DB insert of the installation (installer service lands in Batch 4)
    from app.core.database import AsyncSessionLocal
    from app.models.workflow_pack import WorkflowPackInstallation

    async with AsyncSessionLocal() as db:
        install = WorkflowPackInstallation(
            org_id=oid,
            pack_id=pid,
            release_id=release_id,
            installed_version="1.0.0",
        )
        db.add(install)
        await db.commit()
        return install.id


async def _mock_offering(c, h, oid, capability="image_generation"):
    r = await c.get("/api/v1/providers/adapters", headers=h)
    aid = next(a for a in r.json()["data"] if a["key"] == "mock")["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "Mock"},
        headers=h,
    )
    conn_id = r2.json()["data"]["id"]
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={"connection_id": conn_id, "capability_key": capability, "model_name": "mock-v1"},
        headers=h,
    )
    return r3.json()["data"]["id"]


async def _wait_run(c, h, oid, run_id, target_statuses, tries=40):
    """Poll run detail until it reaches one of the target statuses."""
    for _ in range(tries):
        r = await c.get(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}", headers=h)
        data = r.json()["data"]
        if data["status"] in target_statuses:
            return data
        await asyncio.sleep(0.2)
    return data


# ── Run creation ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_run_validates_inputs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition())

    # Missing required input
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "MISSING_INPUT"

    # Unknown input
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "cats", "hack": "x"}},
        headers=h,
    )
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "UNKNOWN_INPUT"


@pytest.mark.asyncio
async def test_run_completes_simple_pipeline(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition())
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "sunset product shots"}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["id"]

    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    # prompt_template rendered the moustache reference
    assert data["outputs"]["final"] == "Write about sunset product shots"
    # Events audit trail exists
    event_types = [e["event_type"] for e in data["events"]]
    assert "run_created" in event_types
    assert "run_completed" in event_types
    # All steps completed
    assert all(s["status"] == "completed" for s in data["step_runs"])


@pytest.mark.asyncio
async def test_run_idempotency_key(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition())
    key = f"idem-{uuid.uuid4().hex[:8]}"
    body = {"installation_id": install_id, "inputs": {"topic": "x"}, "idempotency_key": key}
    r1 = await c.post(f"/api/v1/orgs/{oid}/workflow-runs", json=body, headers=h)
    r2 = await c.post(f"/api/v1/orgs/{oid}/workflow-runs", json=body, headers=h)
    assert r1.json()["data"]["id"] == r2.json()["data"]["id"]


# ── Provider action ───────────────────────────────────────


@pytest.mark.asyncio
async def test_provider_action_with_mock_adapter(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _mock_offering(c, h, oid)
    install_id = await _install(c, h, oid, _definition(with_provider=True))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "hero image"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    gen = next(s for s in data["step_runs"] if s["step_id"] == "generate")
    assert gen["output"]["result"].startswith("mock-asset-")
    assert gen["offering_id"] is not None  # actual_offering_used recorded


@pytest.mark.asyncio
async def test_provider_action_no_offering_fails(c):
    """No active offering for the capability → NO_ELIGIBLE_PROVIDER, run FAILED."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # No offering created
    install_id = await _install(c, h, oid, _definition(with_provider=True))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "x"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"failed"})
    assert data["status"] == "failed"
    gen = next(s for s in data["step_runs"] if s["step_id"] == "generate")
    assert gen["error_code"] == "NO_ELIGIBLE_PROVIDER"


# ── Review gates ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_review_gate_suspend_approve_resume(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition(with_review=True))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "review me"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]

    # Run suspends at the gate
    data = await _wait_run(c, h, oid, run_id, {"waiting_review"})
    assert data["status"] == "waiting_review"
    qa = next(s for s in data["step_runs"] if s["step_id"] == "qa")
    assert qa["status"] == "waiting_review"

    # An open review exists with a due date
    r2 = await c.get(f"/api/v1/orgs/{oid}/step-reviews", headers=h)
    reviews = r2.json()["data"]
    review = next(rv for rv in reviews if rv["step_run_id"] == qa["id"])
    assert review["due_at"] is not None
    assert review["instructions"] == "Check quality"

    # Approve — synchronous validate-then-accept
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/step-reviews/{review['id']}/decide",
        json={"decision": "approved", "note": "LGTM"},
        headers=h,
    )
    assert r3.status_code == 200
    assert r3.json()["data"]["decision"] == "approved"

    # Double-decide → 409 (durable decision row, partial unique index)
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/step-reviews/{review['id']}/decide",
        json={"decision": "rejected"},
        headers=h,
    )
    assert r4.status_code == 409
    assert r4.json()["error"]["code"] == "WF_REVIEW_ALREADY_DECIDED"

    # Run resumes and completes; review passthrough carries the subject
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    assert data["outputs"]["final"] == "Write about review me"


@pytest.mark.asyncio
async def test_review_gate_reject_fails_run(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition(with_review=True))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "reject me"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"waiting_review"})
    qa = next(s for s in data["step_runs"] if s["step_id"] == "qa")
    r2 = await c.get(f"/api/v1/orgs/{oid}/step-reviews", headers=h)
    review = next(rv for rv in r2.json()["data"] if rv["step_run_id"] == qa["id"])

    await c.post(
        f"/api/v1/orgs/{oid}/step-reviews/{review['id']}/decide",
        json={"decision": "rejected", "note": "Not good enough"},
        headers=h,
    )
    data = await _wait_run(c, h, oid, run_id, {"failed"})
    assert data["status"] == "failed"
    assert data["error_code"] == "WF_STEP_FAILED"
    qa = next(s for s in data["step_runs"] if s["step_id"] == "qa")
    assert qa["status"] == "failed"
    assert qa["error_code"] == "WF_REVIEW_REJECTED"


# ── Cancellation ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_cancel_run_waiting_review(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition(with_review=True))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "cancel me"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    await _wait_run(c, h, oid, run_id, {"waiting_review"})

    r2 = await c.post(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}/cancel", headers=h)
    assert r2.status_code == 200
    assert r2.json()["data"]["status"] == "cancelled"

    # Steps are cancelled, open review expired
    r3 = await c.get(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}", headers=h)
    data = r3.json()["data"]
    qa = next(s for s in data["step_runs"] if s["step_id"] == "qa")
    assert qa["status"] == "cancelled"
    r4 = await c.get(f"/api/v1/orgs/{oid}/step-reviews", headers=h)
    assert not any(rv["step_run_id"] == qa["id"] for rv in r4.json()["data"])

    # Cancel again → 409
    r5 = await c.post(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}/cancel", headers=h)
    assert r5.status_code == 409


# ── Cross-org isolation ───────────────────────────────────


@pytest.mark.asyncio
async def test_run_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    install_id = await _install(c, h1, o1, _definition())
    r = await c.post(
        f"/api/v1/orgs/{o1}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "private"}},
        headers=h1,
    )
    run_id = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.get(f"/api/v1/orgs/{o2}/workflow-runs/{run_id}", headers=h2)
    assert r2.status_code == 404
    # Cannot start a run against another org's installation either
    r3 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "steal"}},
        headers=h2,
    )
    assert r3.status_code == 404


# ── Transform ops ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_transform_concat_text(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = {
        "schema_version": 1,
        "inputs": [
            {"key": "a", "type": "text", "required": True},
            {"key": "b", "type": "text", "required": True},
        ],
        "outputs": [{"key": "joined", "type": "text", "from_step": "join", "from_port": "result"}],
        "steps": [
            {
                "id": "take",
                "type": "asset_input",
                "name": "Take",
                "config": {"accept_types": ["image"]},
                "inputs": [],
                "outputs": [{"port": "a", "type": "text"}, {"port": "b", "type": "text"}],
            },
            {
                "id": "join",
                "type": "transform",
                "name": "Join",
                "config": {"operation": "concat_text", "params": {"separator": " | "}},
                "inputs": [
                    {"port": "x", "type": "text"},
                    {"port": "y", "type": "text"},
                ],
                "outputs": [{"port": "result", "type": "text"}],
            },
        ],
        "edges": [
            {"id": "e1", "from_step": "take", "from_port": "a", "to_step": "join", "to_port": "x"},
            {"id": "e2", "from_step": "take", "from_port": "b", "to_step": "join", "to_port": "y"},
        ],
        "ui": {},
    }
    install_id = await _install(c, h, oid, definition)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"a": "hello", "b": "world"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    assert set(data["outputs"]["joined"].split(" | ")) == {"hello", "world"}


# ── Sweeper recovery (audit fixes) ────────────────────────


@pytest.mark.asyncio
async def test_sweep_exhausted_attempts_fails_step(c):
    """A crashed executor whose step already burned max_attempts must go to
    FAILED WF_RETRY_EXHAUSTED, not loop forever through WAITING_RETRY."""
    from datetime import UTC, datetime, timedelta

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import (
        RunStatus,
        StepRunStatus,
        WorkflowRun,
        WorkflowStepRun,
    )

    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Seed a RUNNING run with a RUNNING step at attempt == max_attempts and
    # an expired lease (simulates an executor that crashed on final attempt)
    async with AsyncSessionLocal() as db:
        run = WorkflowRun(
            org_id=oid,
            definition_snapshot={"steps": [], "edges": [], "inputs": [], "outputs": []},
            inputs={},
            status=RunStatus.RUNNING,
        )
        db.add(run)
        await db.flush()
        sr = WorkflowStepRun(
            run_id=run.id,
            step_id="poison",
            step_type="provider_action",
            status=StepRunStatus.RUNNING,
            attempt=3,
            max_attempts=3,
            lease_expires_at=datetime.now(UTC) - timedelta(minutes=5),
        )
        db.add(sr)
        await db.commit()
        run_id, sr_id = run.id, sr.id

    # GET run detail triggers the lazy sweep
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}", headers=h)
    assert r.status_code == 200

    data = await _wait_run(c, h, oid, run_id, {"failed"})
    assert data["status"] == "failed"
    step = next(s for s in data["step_runs"] if s["id"] == sr_id)
    assert step["status"] == "failed"
    assert step["error_code"] == "WF_RETRY_EXHAUSTED"
    # The sweep must leave an audit trail, not silently mutate step state
    assert any(
        e["event_type"] == "step_failed"
        and e["step_id"] == "poison"
        and e["payload"] == {"error_code": "WF_RETRY_EXHAUSTED"}
        for e in data["events"]
    )


@pytest.mark.asyncio
async def test_sweep_expired_review_fails_run(c):
    """An overdue review must expire, fail the step, AND move the run out of
    WAITING_REVIEW so it settles into FAILED (not stuck forever)."""
    from datetime import UTC, datetime, timedelta

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import WorkflowStepReview

    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition(with_review=True))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "expire me"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"waiting_review"})
    assert data["status"] == "waiting_review"

    # Force the open review past its due date
    qa = next(s for s in data["step_runs"] if s["step_id"] == "qa")
    async with AsyncSessionLocal() as db:
        from sqlalchemy import update as sa_update

        await db.execute(
            sa_update(WorkflowStepReview)
            .where(WorkflowStepReview.step_run_id == qa["id"])
            .values(due_at=datetime.now(UTC) - timedelta(hours=1))
        )
        await db.commit()

    # First GET sweeps (expires review, fails step, resumes run) and
    # re-dispatches; poll until the advance loop settles the run
    await c.get(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}", headers=h)
    data = await _wait_run(c, h, oid, run_id, {"failed"})
    assert data["status"] == "failed"
    qa = next(s for s in data["step_runs"] if s["step_id"] == "qa")
    assert qa["status"] == "failed"
    assert qa["error_code"] == "WF_REVIEW_TIMEOUT"
    # The review row records the expiry, and no open review remains
    r2 = await c.get(f"/api/v1/orgs/{oid}/step-reviews", headers=h)
    assert not any(rv["step_run_id"] == qa["id"] for rv in r2.json()["data"])
    # The sweep leaves an audit trail: review_expired + step_failed events
    event_types = [(e["event_type"], e["step_id"]) for e in data["events"]]
    assert ("review_expired", "qa") in event_types
    assert any(
        e["event_type"] == "step_failed"
        and e["step_id"] == "qa"
        and e["payload"] == {"error_code": "WF_REVIEW_TIMEOUT"}
        for e in data["events"]
    )


@pytest.mark.asyncio
async def test_pinned_binding_with_deleted_offering_hard_stops(c):
    """A pinned binding whose offering was deleted (FK SET NULL) must hard-stop
    with NO_ELIGIBLE_PROVIDER — never silently fall back to auto-selection."""
    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import WorkflowStepBinding

    h, _ = await _auth(c)
    oid = await _org(c, h)
    # An eligible auto candidate EXISTS — the pinned hard-stop must ignore it
    await _mock_offering(c, h, oid)
    install_id = await _install(c, h, oid, _definition(with_provider=True))

    # Seed a pinned binding with offering_id NULL (as left by ondelete=SET NULL)
    async with AsyncSessionLocal() as db:
        db.add(
            WorkflowStepBinding(
                org_id=oid,
                installation_id=install_id,
                step_id="generate",
                binding_mode="pinned",
                offering_id=None,
            )
        )
        await db.commit()

    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "pinned"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"failed"})
    assert data["status"] == "failed"
    gen = next(s for s in data["step_runs"] if s["step_id"] == "generate")
    assert gen["error_code"] == "NO_ELIGIBLE_PROVIDER"


# ── Audit round 2: removed installations + input value validation ──


@pytest.mark.asyncio
async def test_removed_installation_rejects_new_runs(c):
    """A REMOVED installation must not create/execute new runs."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition())

    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import InstallStatus
    from app.models.workflow_pack import WorkflowPackInstallation

    async with AsyncSessionLocal() as db:
        install = await db.get(WorkflowPackInstallation, install_id)
        install.status = InstallStatus.REMOVED
        await db.commit()

    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "nope"}},
        headers=h,
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "INSTALLATION_NOT_FOUND"


@pytest.mark.asyncio
async def test_selection_input_invalid_option_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = _definition()
    definition["inputs"].append(
        {"key": "ratio", "type": "selection", "options": ["1:1", "9:16"], "required": True}
    )
    install_id = await _install(c, h, oid, definition)

    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "x", "ratio": "4:3"}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_INPUT_VALUE"

    # Valid option passes creation
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "x", "ratio": "1:1"}},
        headers=h,
    )
    assert r2.status_code == 201


@pytest.mark.asyncio
async def test_oversized_text_input_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition())
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "y" * 9000}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_INPUT_VALUE"


@pytest.mark.asyncio
async def test_empty_dict_step_output_still_collected(c):
    """A step whose output is {} (instruction steps, adapters returning {})
    must still surface its declared workflow-output key — `if src.output:`
    treated {} as missing and silently dropped the key (audit LOW)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = {
        "schema_version": 1,
        "inputs": [{"key": "topic", "type": "text", "required": True}],
        "outputs": [
            {"key": "final", "type": "text", "from_step": "note", "from_port": "done"}
        ],
        "steps": [
            {
                "id": "note",
                "type": "instruction",
                "name": "Note",
                "config": {"content": "Read the brief"},
                "inputs": [],
                "outputs": [{"port": "done", "type": "text"}],
            }
        ],
        "edges": [],
        "ui": {},
    }
    install_id = await _install(c, h, oid, definition)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "x"}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, ("completed",))
    assert data["status"] == "completed"
    # The key must be PRESENT (value None — instruction steps emit {}),
    # not silently dropped from the outputs dict
    assert "final" in (data["outputs"] or {})


@pytest.mark.asyncio
async def test_admin_sweep_endpoint(c):
    """POST /admin/workflows/sweep — the operator/cron sweep path (the lazy
    sweep only fires for orgs whose runs someone is viewing)."""
    from app.models.user import UserRole

    h, user = await _auth(c)
    oid = await _org(c, h)

    # Promote to platform admin directly
    from app.core.database import AsyncSessionLocal
    from app.models.user import User

    async with AsyncSessionLocal() as db:
        u = await db.get(User, user["id"])
        u.role = UserRole.ADMIN
        await db.commit()

    # Plant a run with an expired lease
    import datetime as _dt

    from app.models.workflow_run import (
        RunStatus,
        StepRunStatus,
        WorkflowRun,
        WorkflowStepRun,
    )

    async with AsyncSessionLocal() as db:
        run = WorkflowRun(
            org_id=oid,
            definition_snapshot={"steps": [], "edges": [], "inputs": [], "outputs": []},
            inputs={},
            status=RunStatus.RUNNING,
        )
        db.add(run)
        await db.flush()
        db.add(
            WorkflowStepRun(
                run_id=run.id,
                step_id="ghost",
                step_type="provider_action",
                status=StepRunStatus.RUNNING,
                attempt=1,
                max_attempts=3,
                lease_expires_at=_dt.datetime.now(_dt.UTC) - _dt.timedelta(minutes=5),
            )
        )
        await db.commit()

        run_id = run.id

    r = await c.post("/api/v1/admin/workflows/sweep", headers=h)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["expired_leases"] >= 1
    assert data["runs_redispatched"] >= 1

    # Lease expiry with attempts remaining leaves a step_lease_expired event
    r2 = await c.get(f"/api/v1/orgs/{oid}/workflow-runs/{run_id}", headers=h)
    events = r2.json()["data"]["events"]
    assert any(
        e["event_type"] == "step_lease_expired"
        and e["step_id"] == "ghost"
        and e["payload"] == {"attempt": 1, "error_code": "WF_EXECUTOR_CRASHED"}
        for e in events
    )


@pytest.mark.asyncio
async def test_admin_sweep_requires_platform_admin(c):
    h, _ = await _auth(c)
    r = await c.post("/api/v1/admin/workflows/sweep", headers=h)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_run_input_with_nul_rejected(c):
    """A NUL in a run input value would crash asyncpg on the JSONB insert
    (500). create_run must reject it as INVALID_INPUT_VALUE (422)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    install_id = await _install(c, h, oid, _definition())
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "a" + chr(0) + "b"}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_INPUT_VALUE"


# ── Audit round 3: output-step mapping, skip fixpoint, bindings, NUL outputs ──


@pytest.mark.asyncio
async def test_output_step_maps_input_to_declared_output_port(c):
    """An output step's result must be keyed by its DECLARED OUTPUT port —
    downstream collection reads by output port and the duplicate-port rule
    makes input/output names disjoint, so input-port keys lose the value."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = _definition()
    definition["steps"].append(
        {
            "id": "deliver",
            "type": "output",
            "name": "Deliver",
            "config": {},
            "inputs": [{"port": "incoming", "type": "prompt"}],
            "outputs": [{"port": "delivered", "type": "prompt"}],
        }
    )
    definition["edges"].append(
        {"id": "e9", "from_step": "build_prompt", "from_port": "prompt", "to_step": "deliver", "to_port": "incoming"}
    )
    definition["outputs"] = [
        {"key": "final", "type": "prompt", "from_step": "deliver", "from_port": "delivered"}
    ]
    install_id = await _install(c, h, oid, definition)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "port mapping"}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    # The value must arrive under the OUTPUT port key — a real string, not None
    assert data["outputs"]["final"] == "Write about port mapping"
    deliver = next(s for s in data["step_runs"] if s["step_id"] == "deliver")
    assert deliver["output"] == {"delivered": "Write about port mapping"}


@pytest.mark.asyncio
async def test_skip_propagation_settles_multihop_chain_in_one_advance(c):
    """Reverse-topological chain c(FAILED)->b->a: the skip-propagation
    fixpoint must settle the run FAILED within a single advance_run call —
    without needing extra externally-triggered advances."""
    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import (
        RunStatus,
        StepRunStatus,
        WorkflowRun,
        WorkflowStepRun,
    )
    from app.services.workflow_runtime import advance_run

    h, _ = await _auth(c)
    oid = await _org(c, h)

    definition = {
        "schema_version": 1,
        "inputs": [],
        "outputs": [],
        "steps": [
            {"id": s, "type": "instruction", "name": s.upper(), "config": {"content": "x"},
             "inputs": [{"port": "trigger", "type": "text", "required": False}] if s != "c" else [],
             "outputs": [{"port": "done", "type": "text"}]}
            for s in ("a", "b", "c")
        ],
        "edges": [
            {"id": "e1", "from_step": "c", "from_port": "done", "to_step": "b", "to_port": "trigger"},
            {"id": "e2", "from_step": "b", "from_port": "done", "to_step": "a", "to_port": "trigger"},
        ],
    }
    # Seed: c FAILED, b/a PENDING, run RUNNING. Step rows inserted a,b,c so
    # dict iteration is reverse-topological — a single pass would only skip b.
    async with AsyncSessionLocal() as db:
        run = WorkflowRun(
            org_id=oid, definition_snapshot=definition, inputs={}, status=RunStatus.RUNNING
        )
        db.add(run)
        await db.flush()
        for sid in ("a", "b"):
            db.add(
                WorkflowStepRun(
                    run_id=run.id, step_id=sid, step_type="instruction",
                    status=StepRunStatus.PENDING, max_attempts=3,
                )
            )
        db.add(
            WorkflowStepRun(
                run_id=run.id, step_id="c", step_type="instruction",
                status=StepRunStatus.FAILED, error_code="WF_STEP_ERROR", max_attempts=3,
            )
        )
        await db.commit()
        run_id = run.id

    # ONE advance_run call must fully settle the run
    await advance_run(run_id)

    async with AsyncSessionLocal() as db:
        settled = await db.get(WorkflowRun, run_id)
        assert settled.status == RunStatus.FAILED
        from sqlalchemy import select as sa_select

        srs = (
            await db.execute(
                sa_select(WorkflowStepRun).where(WorkflowStepRun.run_id == run_id)
            )
        ).scalars().all()
        by_id = {s.step_id: s.status for s in srs}
        assert by_id["c"] == StepRunStatus.FAILED
        assert by_id["b"] == StepRunStatus.SKIPPED
        assert by_id["a"] == StepRunStatus.SKIPPED


@pytest.mark.asyncio
async def test_unconfirmed_binding_suggestion_falls_through_to_auto(c):
    """An UNCONFIRMED suggestion row (confirmed_by=None) must NOT freeze the
    org on the at-install offering — the auto rung re-selects the cheapest
    eligible offering every run."""
    from sqlalchemy import update as sa_update

    from app.core.database import AsyncSessionLocal
    from app.models.provider import ProviderModelOffering
    from app.models.workflow_run import WorkflowStepBinding

    h, _ = await _auth(c)
    oid = await _org(c, h)
    expensive_id = await _mock_offering(c, h, oid)
    install_id = await _install(c, h, oid, _definition(with_provider=True))

    # Unconfirmed suggestion pointing at the (only, expensive) offering
    async with AsyncSessionLocal() as db:
        await db.execute(
            sa_update(ProviderModelOffering)
            .where(ProviderModelOffering.id == expensive_id)
            .values(cost_per_call_usd=9.99)
        )
        db.add(
            WorkflowStepBinding(
                org_id=oid,
                installation_id=install_id,
                step_id="generate",
                binding_mode="auto",
                offering_id=expensive_id,
                confirmed_by=None,  # unconfirmed suggestion (D5)
            )
        )
        await db.commit()

    # A cheaper offering added AFTER install must win via the auto rung
    cheap_id = await _mock_offering(c, h, oid)
    async with AsyncSessionLocal() as db:
        await db.execute(
            sa_update(ProviderModelOffering)
            .where(ProviderModelOffering.id == cheap_id)
            .values(cost_per_call_usd=0.01)
        )
        await db.commit()

    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "auto rung"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    gen = next(s for s in data["step_runs"] if s["step_id"] == "generate")
    assert gen["offering_id"] == cheap_id  # auto re-selected, not the frozen suggestion


@pytest.mark.asyncio
async def test_confirmed_binding_with_stale_features_falls_through(c):
    """A CONFIRMED binding whose offering no longer satisfies the step's
    required_features is stale: non-pinned mode falls through to auto."""
    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import WorkflowStepBinding

    h, user = await _auth(c)
    oid = await _org(c, h)
    # Offering WITHOUT the required feature (features default [])
    bare_id = await _mock_offering(c, h, oid)
    definition = _definition(with_provider=True)
    definition["steps"][2]["config"]["required_features"] = ["hires"]
    install_id = await _install(c, h, oid, definition)

    # Confirmed (human) binding pointing at the featureless offering
    async with AsyncSessionLocal() as db:
        db.add(
            WorkflowStepBinding(
                org_id=oid,
                installation_id=install_id,
                step_id="generate",
                binding_mode="preferred",
                offering_id=bare_id,
                confirmed_by=user["id"],
            )
        )
        await db.commit()

    # No eligible auto candidate either → NO_ELIGIBLE_PROVIDER (proves the
    # stale confirmed binding was NOT used)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "stale features"}},
        headers=h,
    )
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"failed"})
    assert data["status"] == "failed"
    gen = next(s for s in data["step_runs"] if s["step_id"] == "generate")
    assert gen["error_code"] == "NO_ELIGIBLE_PROVIDER"


@pytest.mark.asyncio
async def test_step_output_with_nul_fails_step_cleanly(c):
    """Adapter output containing NUL must fail the step WF_OUTPUT_INVALID and
    settle the run FAILED — never crash the JSONB write (500 / stranded
    RUNNING step with a live lease)."""
    from app.services import workflow_adapters as wa

    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _mock_offering(c, h, oid)
    install_id = await _install(c, h, oid, _definition(with_provider=True))

    class NulAdapter(wa.ProviderAdapterBase):
        key = "mock"

        async def execute(self, capability, model_name, inputs, config, credentials, idempotency_key):
            return {"result": "a\x00b"}

    original = wa._ADAPTERS["mock"]
    wa._ADAPTERS["mock"] = NulAdapter()
    try:
        r = await c.post(
            f"/api/v1/orgs/{oid}/workflow-runs",
            json={"installation_id": install_id, "inputs": {"topic": "nul output"}},
            headers=h,
        )
        assert r.status_code == 201, r.text
        run_id = r.json()["data"]["id"]
        data = await _wait_run(c, h, oid, run_id, {"failed", "completed"})
    finally:
        wa._ADAPTERS["mock"] = original

    assert data["status"] == "failed", data
    gen = next(s for s in data["step_runs"] if s["step_id"] == "generate")
    assert gen["status"] == "failed"
    assert gen["error_code"] == "WF_OUTPUT_INVALID"


@pytest.mark.asyncio
async def test_json_input_default_applied_as_parsed_json(c):
    """A json-typed input with a valid string default must run: create_run
    parses the default instead of tripping its own type check (422 brick)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = _definition()
    definition["inputs"].append(
        {"key": "cfg", "type": "json", "required": True, "default": '{"size": "1024"}'}
    )
    install_id = await _install(c, h, oid, definition)

    # Omit 'cfg' — the default must apply, parsed, and the run completes
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "defaults"}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    assert data["inputs"]["cfg"] == {"size": "1024"}


@pytest.mark.asyncio
async def test_template_ref_orders_execution_without_edge(c):
    """A prompt_template referencing a LATER step with no edge must wait for
    the ref target and render real content — not '' from an unready ref."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = {
        "schema_version": 1,
        "inputs": [{"key": "topic", "type": "text", "required": True}],
        "outputs": [
            {"key": "final", "type": "prompt", "from_step": "reporter", "from_port": "out"}
        ],
        "steps": [
            # 'reporter' is FIRST in definition order but data-depends on
            # 'source' via a moustache ref only (no edge)
            {
                "id": "reporter",
                "type": "prompt_template",
                "name": "Reporter",
                "config": {"template": "Source said: {{steps.source.outputs.text}}"},
                "inputs": [],
                "outputs": [{"port": "out", "type": "prompt"}],
            },
            {
                "id": "source",
                "type": "prompt_template",
                "name": "Source",
                "config": {"template": "value-{{inputs.topic}}"},
                "inputs": [],
                "outputs": [{"port": "text", "type": "prompt"}],
            },
        ],
        "edges": [],
        "ui": {},
    }
    install_id = await _install(c, h, oid, definition)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"topic": "ordering"}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    # The referenced value must be REAL content, not the empty string an
    # unready ref would have rendered
    assert data["outputs"]["final"] == "Source said: value-ordering"


# ── Audit round 16: cancel-race event, JSON template rendering ──


@pytest.mark.asyncio
async def test_cancel_lost_race_records_no_event(c):
    """cancel_run losing the race to a concurrent completion (run UPDATE
    rowcount 0) must NOT fabricate a run_cancelled event — the run was never
    cancelled."""
    import json as _json
    from datetime import UTC, datetime

    from sqlalchemy import update as sa_update

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import RunStatus, WorkflowRun
    from app.services.workflow_runtime import WorkflowRuntimeService

    h, _ = await _auth(c)
    oid = await _org(c, h)

    async with AsyncSessionLocal() as db:
        run = WorkflowRun(
            org_id=oid,
            definition_snapshot={"steps": [], "edges": [], "inputs": [], "outputs": []},
            inputs={},
            status=RunStatus.RUNNING,
        )
        db.add(run)
        await db.commit()
        run_id = run.id

    async with AsyncSessionLocal() as db:
        svc = WorkflowRuntimeService(db)
        # Pre-load into the identity map so cancel_run's terminal-state check
        # sees the stale RUNNING status (the classic race window)
        stale = await db.get(WorkflowRun, run_id)
        assert stale.status == RunStatus.RUNNING

        # A concurrent executor completes the run in its own session
        async with AsyncSessionLocal() as db2:
            await db2.execute(
                sa_update(WorkflowRun)
                .where(WorkflowRun.id == run_id)
                .values(status=RunStatus.COMPLETED, finished_at=datetime.now(UTC))
            )
            await db2.commit()

        run = await svc.cancel_run(run_id, oid)
        await db.commit()
        # The guarded UPDATE lost — the run stays completed
        assert run.status == RunStatus.COMPLETED

    async with AsyncSessionLocal() as db:
        svc = WorkflowRuntimeService(db)
        events = await svc.get_events(run_id)
        assert not any(e.event_type == "run_cancelled" for e in events), _json.dumps(
            [e.event_type for e in events]
        )


@pytest.mark.asyncio
async def test_template_renders_json_input_as_valid_json(c):
    """A json-typed input rendered into a prompt_template must produce valid
    JSON text — str() would emit Python repr (single quotes, True/None) and
    silently corrupt any JSON payload the template builds."""
    import json as _json

    h, _ = await _auth(c)
    oid = await _org(c, h)
    definition = {
        "schema_version": 1,
        "inputs": [{"key": "cfg", "type": "json", "required": True}],
        "outputs": [
            {"key": "final", "type": "prompt", "from_step": "build", "from_port": "out"}
        ],
        "steps": [
            {
                "id": "build",
                "type": "prompt_template",
                "name": "Build",
                "config": {"template": '{"payload": {{inputs.cfg}}}'},
                "inputs": [],
                "outputs": [{"port": "out", "type": "prompt"}],
            }
        ],
        "edges": [],
        "ui": {},
    }
    install_id = await _install(c, h, oid, definition)
    cfg = {"size": "1024", "tags": ["a", "b"], "hd": True, "note": None}
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": install_id, "inputs": {"cfg": cfg}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["id"]
    data = await _wait_run(c, h, oid, run_id, {"completed", "failed"})
    assert data["status"] == "completed", data
    # The rendered template must parse as JSON and round-trip the input
    assert _json.loads(data["outputs"]["final"]) == {"payload": cfg}


@pytest.mark.asyncio
async def test_deep_nested_run_input_no_recursion_error(c):
    """R20: the run-input ctrl screen (_values_have_ctrl) was still recursive
    after R18 fixed its comfyui/matching siblings — a deep JSON input
    RecursionError'd into a 500. Iterative now: never a 500.

    The input MUST be json-typed: the per-type check runs BEFORE the ctrl
    scan, and a text/asset input rejects a non-str value at the type check
    (422) so the scanner is never reached — the original test fed a
    text-typed input and thus guarded NOTHING (reverting the fix left it
    green). A json-typed value passes the type+size gate (dict/list,
    len(str) <= 8000) and IS scanned, so depth ~3990 (str len ~7983) is the
    reachable path the recursive version blew up on (R35)."""
    import json as _j

    # A json input step so the value reaches _values_have_ctrl
    defn = {
        "schema_version": 1,
        "inputs": [{"key": "cfg", "type": "json", "required": True}],
        "outputs": [{"key": "out", "type": "json", "from_step": "echo", "from_port": "o"}],
        "steps": [
            {
                "id": "take",
                "type": "asset_input",
                "name": "Take",
                "config": {"accept_types": []},
                "inputs": [],
                "outputs": [{"port": "cfg", "type": "json"}],
            },
            {
                "id": "echo",
                "type": "output",
                "name": "Echo",
                "config": {},
                "inputs": [{"port": "i", "type": "json"}],
                "outputs": [{"port": "o", "type": "json"}],
            },
        ],
        "edges": [{"id": "e1", "from_step": "take", "from_port": "cfg", "to_step": "echo", "to_port": "i"}],
        "ui": {},
    }
    h, _ = await _auth(c)
    oid = await _org(c, h)
    inst_id = await _install(c, h, oid, defn)
    # A json value under the 8000-char size gate but deeply nested. Two
    # distinct 500 paths this must NOT hit: (a) the run-input ctrl scanner
    # (recursive pre-R20 → RecursionError at depth ~500), and (b) the
    # response serializer echoing inputs (pydantic recursion guard ~400).
    # The R35 depth gate rejects both as a clean 422 well below either limit.
    deep = _j.loads("[" * 900 + '"x"' + "]" * 900)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": inst_id, "inputs": {"cfg": deep}},
        headers=h,
    )
    # Clean 422 (too deep) — the regression under test is: NEVER a 500.
    assert r.status_code == 422, f"{r.status_code}: {r.text[:200]}"
    assert r.json()["error"]["code"] == "INVALID_INPUT_VALUE"

    # And a shallow json value still runs cleanly (the gate isn't over-broad)
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-runs",
        json={"installation_id": inst_id, "inputs": {"cfg": {"width": 512}}},
        headers=h,
    )
    assert r2.status_code == 201, f"{r2.status_code}: {r2.text[:200]}"


def test_transform_values_follow_declared_port_order():
    """R43: concat_text joins by the step's DECLARED input-port order, not
    by edge-array insertion order. inputs_resolved is keyed in edge order —
    the old list(inputs.values()) made "hello | world" vs "world | hello"
    depend on which edge the author happened to draw first, and select_field
    silently switched source ports on an unrelated edge reorder."""
    from app.services.workflow_runtime import _run_transform

    step = {
        "id": "join",
        "type": "transform",
        "inputs": [{"port": "x", "type": "text"}, {"port": "y", "type": "text"}],
        "outputs": [{"port": "result", "type": "text"}],
    }
    # Resolved dict keyed in REVERSED edge order (y's edge drawn first)
    inputs_edge_order = {"y": "world", "x": "hello"}
    out = _run_transform(
        {"operation": "concat_text", "params": {"separator": " | "}},
        inputs_edge_order,
        step,
    )
    assert out["result"] == "hello | world"

    # select_field's "first input" is the first DECLARED port (x), not the
    # first-drawn edge (y)
    out2 = _run_transform(
        {"operation": "select_field", "params": {"field": "k"}},
        {"y": '{"k": "from_y"}', "x": '{"k": "from_x"}'},
        step,
    )
    assert out2["result"] == "from_x"

    # Unconnected declared port injects no None padding
    out3 = _run_transform(
        {"operation": "concat_text", "params": {"separator": "+"}},
        {"y": "only"},
        step,
    )
    assert out3["result"] == "only"
