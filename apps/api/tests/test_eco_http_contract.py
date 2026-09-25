"""Round-32 tests (ADR-016 §39): HTTP-layer authz matrix + response contract.

The recurring authz classes (403-vs-404 oracles, missing owner gates, role
gates) are only provable at the HTTP layer — service tests never exercise
dependency wiring. This suite pins: anonymous → 401 everywhere; member → 403
on admin-only surfaces; member reads → 200 with the {data: ...} envelope;
errors → {error: {code, message}} shape.
"""

from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.main import app
from tests.test_eco_services_db import _mk_user

# Read surfaces any authenticated member may use
MEMBER_READ_PATHS = [
    "/api/v1/ecosystem/dashboard",
    "/api/v1/ecosystem/dashboard/coverage",
    "/api/v1/ecosystem/dashboard/trending",
    "/api/v1/ecosystem/catalog/models",
    "/api/v1/ecosystem/changes",
    "/api/v1/ecosystem/benchmark/leaderboard",
    "/api/v1/ecosystem/benchmark/runs",
    "/api/v1/ecosystem/security/advisories",
    "/api/v1/ecosystem/watchlists",
    "/api/v1/ecosystem/pricing/observations",
    "/api/v1/ecosystem/deprecation-calendar",
    "/api/v1/ecosystem/pricing/history?entity_kind=model&entity_id=" + "0" * 26,
    "/api/v1/ecosystem/pricing/availability/uptime?entity_kind=model&entity_id=" + "0" * 26,
    "/api/v1/ecosystem/benchmark/score-history?entity_kind=model&entity_id=" + "0" * 26,
    "/api/v1/ecosystem/export/changes?since=2026-01-01T00:00:00%2B00:00",
]

# Platform-admin-only surfaces (member must see 403, never data)
ADMIN_ONLY = [
    ("GET", "/api/v1/ecosystem/audit", None),
    ("GET", "/api/v1/ecosystem/audit.csv", None),
    ("GET", "/api/v1/ecosystem/catalog/models/duplicates", None),
    ("GET", "/api/v1/ecosystem/impact/analyses/" + "0" * 26, None),
    ("POST", "/api/v1/ecosystem/sources", {"name": "x", "source_type": "vendor_api",
                                           "trust_level": "official", "adapter_key": "manual"}),
    ("POST", "/api/v1/ecosystem/security/advisories",
     {"advisory_ref": "CVE-X", "title": "t", "severity": "high", "affected_ref": "y"}),
    ("POST", "/api/v1/ecosystem/benchmark/suites",
     {"key": "kx", "name": "n", "family": "image_generation", "capability_key": "c"}),
    ("POST", "/api/v1/ecosystem/sources/" + "0" * 26 + "/replay", None),
    ("POST", "/api/v1/ecosystem/benchmark/suites/import",
     {"format": "openskill.benchmark-suite", "version": 1, "suite": {}, "cases": []}),
    ("POST", "/api/v1/ecosystem/security/advisories/" + "0" * 26 + "/status?to_status=mitigated", None),
]


@pytest.fixture
async def http():
    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as c:
        yield c
    app.router.lifespan_context = orig


@pytest.fixture
async def tokens():
    """A committed member + admin token pair (visible to request sessions)."""
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        member = await _mk_user(db)
        admin = await _mk_user(db, "admin")
        await db.commit()
        yield {
            "member": create_access_token(member.id, member.email, member.role.value),
            "admin": create_access_token(admin.id, admin.email, admin.role.value),
        }
    await engine.dispose()


async def test_anonymous_gets_401_everywhere(http):
    for path in MEMBER_READ_PATHS:
        r = await http.get(path)
        assert r.status_code == 401, f"{path} -> {r.status_code}"
        body = r.json()
        assert "error" in body and body["error"]["code"], path
    for method, path, payload in ADMIN_ONLY:
        r = await http.request(method, path, json=payload)
        assert r.status_code == 401, f"{method} {path} -> {r.status_code}"


async def test_member_reads_return_data_envelope(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    for path in MEMBER_READ_PATHS:
        r = await http.get(path, headers=headers)
        assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
        assert "data" in r.json(), path


async def test_member_can_read_atom_feed(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/export/changes.atom", headers=headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/atom+xml")
    assert r.text.startswith("<?xml")


async def test_member_blocked_from_admin_surfaces(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    for method, path, payload in ADMIN_ONLY:
        r = await http.request(method, path, json=payload, headers=headers)
        assert r.status_code == 403, f"{method} {path} -> {r.status_code}: {r.text[:200]}"


async def test_error_shapes_are_machine_readable(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    # Unknown catalog kind → uniform 404 with machine code
    r = await http.get("/api/v1/ecosystem/catalog/nonsense-kind", headers=headers)
    assert r.status_code == 404
    assert r.json()["error"]["code"]
    # compare with too few ids → 422 VALIDATION_ERROR
    r = await http.get(
        "/api/v1/ecosystem/compare", params={"kind": "model", "ids": "a"}, headers=headers
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    # Nonexistent entity scorecard → uniform 404, no existence oracle
    r = await http.get(
        f"/api/v1/ecosystem/catalog/models/{'0' * 26}/scorecard", headers=headers
    )
    assert r.status_code == 404

CORE_ENDPOINTS = {
    # (method, path) pairs that MUST exist — removing one is a breaking change.
    ("POST", "/api/v1/ecosystem/sources"),
    ("POST", "/api/v1/ecosystem/sources/{source_id}/sync"),
    ("GET", "/api/v1/ecosystem/observations"),
    ("GET", "/api/v1/ecosystem/changes"),
    ("GET", "/api/v1/ecosystem/catalog/{segment}"),
    ("GET", "/api/v1/ecosystem/catalog/{segment}/{entity_id}/scorecard"),
    ("GET", "/api/v1/ecosystem/catalog/{segment}/duplicates"),
    ("GET", "/api/v1/ecosystem/compare"),
    ("POST", "/api/v1/ecosystem/pricing/estimate"),
    ("GET", "/api/v1/ecosystem/pricing/history"),
    ("GET", "/api/v1/ecosystem/pricing/availability/uptime"),
    ("GET", "/api/v1/ecosystem/benchmark/leaderboard"),
    ("GET", "/api/v1/ecosystem/benchmark/score-history"),
    ("POST", "/api/v1/ecosystem/benchmark/runs/{run_id}/cancel"),
    ("GET", "/api/v1/ecosystem/benchmark/suites/{suite_id}/export"),
    ("POST", "/api/v1/ecosystem/benchmark/suites/import"),
    ("POST", "/api/v1/ecosystem/watchlists/quick-watch"),
    ("PATCH", "/api/v1/ecosystem/watchlists/{watchlist_id}"),
    ("GET", "/api/v1/ecosystem/dashboard"),
    ("GET", "/api/v1/ecosystem/dashboard/coverage"),
    ("GET", "/api/v1/ecosystem/dashboard/trending"),
    ("GET", "/api/v1/ecosystem/export/changes"),
    ("GET", "/api/v1/ecosystem/export/changes.atom"),
    ("GET", "/api/v1/ecosystem/audit"),
    ("GET", "/api/v1/ecosystem/audit.csv"),
    ("GET", "/api/v1/ecosystem/ops/metrics"),
    ("POST", "/api/v1/ecosystem/security/advisories"),
    ("GET", "/api/v1/ecosystem/security/advisories/{advisory_id}/affected"),
    ("GET", "/api/v1/ecosystem/deprecation-calendar.ics"),
}


def test_core_ecosystem_api_surface_is_stable():
    """API-contract bar: the core eco surface may only GROW. A missing pair
    here means a breaking change shipped without a deliberate decision."""
    from app.main import app

    spec = app.openapi()
    present = {
        (method.upper(), path)
        for path, ops in spec["paths"].items()
        if "/ecosystem" in path
        for method in ops
        if method.lower() in ("get", "post", "put", "patch", "delete")
    }
    missing = CORE_ENDPOINTS - present
    assert not missing, f"Breaking API change — endpoints gone: {sorted(missing)}"

async def test_org_scoped_reads_require_membership(http, tokens):
    """Cross-tenant guard (round 79): a member passing an ARBITRARY org_id to
    graph-node or drafts listings must be refused (403/404) — org-scoped
    private edges and draft payloads are tenant-confidential."""
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    foreign_org = "0" * 26
    r = await http.get(
        f"/api/v1/ecosystem/graph/node/model/{'1' * 26}?org_id={foreign_org}",
        headers=headers,
    )
    assert r.status_code in (403, 404), r.text[:200]
    r = await http.get(
        f"/api/v1/ecosystem/drafts?org_id={foreign_org}", headers=headers
    )
    assert r.status_code in (403, 404), r.text[:200]
    # Without org_id both remain readable (public/global scope)
    r = await http.get(f"/api/v1/ecosystem/graph/node/model/{'1' * 26}", headers=headers)
    assert r.status_code == 200
    r = await http.get("/api/v1/ecosystem/drafts", headers=headers)
    assert r.status_code == 200

async def test_org_scoped_draft_single_read_and_watchlist_attach_guarded(http, tokens):
    """Round-80 guards: (a) an org-scoped draft read by id is a UNIFORM 404
    for non-members (list was fixed in §66; the by-id path leaked payloads);
    (b) creating a watchlist attached to a foreign org is refused — org
    attachment drives that org's webhook fan-out."""
    from app.core.database import AsyncSessionLocal, engine
    from app.ecosystem.services.drafts import DraftService
    from tests.test_eco_services_db import _mk_org, _mk_user

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        admin = await _mk_user(db, "admin")
        org = await _mk_org(db)
        draft = await DraftService(db).create(
            draft_type="skill_pack_update", title="tenant-secret",
            payload={"target_pack_id": "P" * 26, "suggestions": [{"kind": "lesson"}]},
            created_by=admin.id, org_id=org.id,
        )
        await db.commit()
        draft_id, org_id = draft.id, org.id
    await engine.dispose()

    member_headers = {"Authorization": f"Bearer {tokens['member']}"}
    admin_headers = {"Authorization": f"Bearer {tokens['admin']}"}

    # (a) non-member by-id read → uniform 404, never the payload
    r = await http.get(f"/api/v1/ecosystem/drafts/{draft_id}", headers=member_headers)
    assert r.status_code == 404, r.text[:200]
    assert "tenant-secret" not in r.text
    # platform admin still reads it
    r = await http.get(f"/api/v1/ecosystem/drafts/{draft_id}", headers=admin_headers)
    assert r.status_code == 200

    # (b) foreign-org watchlist attach refused
    r = await http.post(
        "/api/v1/ecosystem/watchlists",
        json={"name": "spy", "org_id": org_id},
        headers=member_headers,
    )
    assert r.status_code in (403, 404), r.text[:200]
    # org-less watchlist creation still works
    r = await http.post(
        "/api/v1/ecosystem/watchlists", json={"name": "mine"}, headers=member_headers
    )
    assert r.status_code == 201

async def test_query_parameter_boundaries(http, tokens):
    """Round-92 boundary contract: malformed/out-of-range query params are
    clean 4xx with the machine envelope — never 500s."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    admin = {"Authorization": f"Bearer {tokens['admin']}"}

    # Malformed ISO 'since' → 4xx envelope
    r = await http.get(
        "/api/v1/ecosystem/export/changes?since=not-a-date", headers=member
    )
    assert 400 <= r.status_code < 500
    assert "error" in r.json()
    # uptime days out of range → 422
    r = await http.get(
        "/api/v1/ecosystem/pricing/availability/uptime"
        "?entity_kind=model&entity_id=" + "0" * 26 + "&days=9999",
        headers=member,
    )
    assert r.status_code == 422
    # NaN workload quantity → 4xx, never 500
    raw = (
        '{"entity_kind":"model","entity_ids":["' + "0" * 26 + '"],'
        '"workload":{"token_input":NaN}}'
    )
    r = await http.post(
        "/api/v1/ecosystem/pricing/estimate",
        content=raw,
        headers={**member, "content-type": "application/json"},
    )
    assert 400 <= r.status_code < 500, r.text[:200]
    # audit.csv limit above cap → 422
    r = await http.get("/api/v1/ecosystem/audit.csv?limit=999999", headers=admin)
    assert r.status_code == 422

async def test_manual_observation_input_hygiene(http, tokens):
    """Round-102 killers ×4: manual observations validate event_type against
    the enum, refuse non-http(s) provenance (rendered as a link), screen
    external_ref, and bound the normalized payload."""
    admin = {"Authorization": f"Bearer {tokens['admin']}"}
    r = await http.post(
        "/api/v1/ecosystem/sources",
        json={
            "name": f"manual-hygiene-{uuid4().hex[:16]}",
            "source_type": "manual_analyst",
            "trust_level": "official",
            "adapter_key": "manual",
        },
        headers=admin,
    )
    assert r.status_code == 201, r.text
    source_id = r.json()["data"]["id"]
    base = {"source_id": source_id, "event_type": "price_changed"}

    r = await http.post("/api/v1/ecosystem/observations",
                        json={**base, "event_type": "totally_made_up"}, headers=admin)
    assert r.status_code == 422
    r = await http.post("/api/v1/ecosystem/observations",
                        json={**base, "provenance_url": "javascript:alert(1)"}, headers=admin)
    assert r.status_code == 422
    r = await http.post("/api/v1/ecosystem/observations",
                        json={**base, "normalized": {"blob": "x" * 120_000}}, headers=admin)
    assert r.status_code == 422
    r = await http.post("/api/v1/ecosystem/observations",
                        json={**base, "external_ref": "ref\u0000evil"}, headers=admin)
    assert r.status_code == 201
    assert "\u0000" not in (r.json()["data"]["external_ref"] or "")

async def test_documented_alert_metrics_are_emitted(http, tokens):
    """Round-118 killer: every eco_* metric named in the ops runbook
    (docs/ops/ecosystem-alerts.md) must actually be emitted by
    /ecosystem/ops/metrics — a renamed metric silently kills its alert."""
    import re
    from pathlib import Path

    doc = Path(__file__).resolve().parents[3] / "docs" / "ops" / "ecosystem-alerts.md"
    documented = set(re.findall(r"eco_[a-z0-9_]+", doc.read_text()))
    # cron job names mentioned in runbook prose, not metrics
    documented -= {"eco_impact_sla", "eco_sync_sweep", "eco_retention", "eco_rollout_eval", "eco_stuck_runs"}
    assert documented, "runbook lists no metrics — path wrong?"

    admin = {"Authorization": f"Bearer {tokens['admin']}"}
    r = await http.get("/api/v1/ecosystem/ops/metrics", headers=admin)
    assert r.status_code == 200
    emitted = set(re.findall(r"^eco_[a-z0-9_]+", r.text, flags=re.M))
    missing = {m.rstrip("_") for m in documented} - emitted
    # trailing-digit windows like eco_discoveries_7d are emitted verbatim
    missing = {m for m in missing if m not in emitted}
    assert not missing, f"runbook metrics not emitted: {sorted(missing)}"

def test_all_eco_limit_params_are_bounded():
    """Round-122 systemic guard: every `limit` query parameter on an
    /ecosystem endpoint must declare a maximum (an unbounded limit is a
    one-request table dump / OOM lever). Applies to future endpoints too."""
    from app.main import app

    spec = app.openapi()
    offenders = []
    for path, ops in spec["paths"].items():
        if "/ecosystem" not in path:
            continue
        for op in ops.values():
            if not isinstance(op, dict):
                continue
            for param in op.get("parameters", []):
                if param.get("name") != "limit" or param.get("in") != "query":
                    continue
                schema = param.get("schema", {})
                # anyOf for optional ints
                schemas = schema.get("anyOf", [schema])
                if not any("maximum" in s for s in schemas if isinstance(s, dict)):
                    offenders.append(f"{path} [{op.get('operationId')}]")
    assert not offenders, f"unbounded limit params: {offenders}"

def test_all_mutating_eco_routes_require_a_user():
    """Round-123 systemic guard: EVERY /ecosystem route (reads included) must
    resolve a User dependency (get_current_user / require_platform_admin) —
    a future endpoint that forgets auth fails HERE, not in prod."""
    from fastapi.routing import APIRoute

    from app.main import app

    def dependant_names(dep, acc):
        acc.add(getattr(dep.call, "__name__", ""))
        for sub in dep.dependencies:
            dependant_names(sub, acc)
        return acc

    offenders = []
    for route in app.routes:
        if not isinstance(route, APIRoute) or "/ecosystem" not in route.path:
            continue
        methods = route.methods & {"GET", "POST", "PATCH", "DELETE", "PUT"}
        if not methods:
            continue
        names = dependant_names(route.dependant, set())
        if not ({"get_current_user", "require_platform_admin"} & names):
            offenders.append(f"{sorted(methods)} {route.path}")
    assert not offenders, f"eco routes without a user dependency: {offenders}"

def test_app_error_code_status_consistency():
    """Round-139 systemic guard: every literal AppError(code, msg, status) in
    the ecosystem package pairs its machine code with the matching HTTP
    status — a NOT_FOUND that ships as 403 (or a VALIDATION_ERROR as 500)
    breaks every client that switches on the code."""
    import ast
    from pathlib import Path

    base = Path(__file__).resolve().parents[1] / "app" / "ecosystem"
    expect = {
        "NOT_FOUND": {404},
        "VALIDATION_ERROR": {422},
        "ECO_INVALID_TRANSITION": {409},
        "ECO_RATE_LIMITED": {429},
        "ECO_SYNC_IN_PROGRESS": {409},
        "FORBIDDEN": {403},
    }
    bad = []
    for f in base.rglob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            if (
                isinstance(node, ast.Call)
                and getattr(node.func, "id", "") == "AppError"
                and len(node.args) >= 3
            ):
                code, status = node.args[0], node.args[2]
                if isinstance(code, ast.Constant) and isinstance(status, ast.Constant):
                    want = expect.get(code.value)
                    if want and status.value not in want:
                        bad.append(f"{f.name}:{node.lineno} {code.value} -> {status.value}")
    assert not bad, f"AppError code/status mismatches: {bad}"

async def test_bulk_acknowledge_changes(http, tokens):
    """Round-174 killer: bulk-acknowledge drains the triage queue idempotently
    — missing ids reported, second call a no-op, route ordering must not let
    the literal path be captured by /{change_id}/acknowledge."""
    admin = {"Authorization": f"Bearer {tokens['admin']}"}
    r = await http.post(
        "/api/v1/ecosystem/changes/bulk-acknowledge",
        json={"ids": ["0" * 26]},
        headers=admin,
    )
    assert r.status_code == 200, r.text
    body = r.json()["data"]
    assert body["acknowledged"] == []
    assert body["missing"] == ["0" * 26]

async def test_delta_since_id_is_validated_over_http(http, tokens):
    """Round-197: the composite-cursor params validate at the HTTP boundary —
    a malformed since_id is a 422, and a valid pair round-trips."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get(
        "/api/v1/ecosystem/export/changes",
        params={"since": "2026-01-01T00:00:00Z", "since_id": "short"},
        headers=member,
    )
    assert r.status_code == 422
    r = await http.get(
        "/api/v1/ecosystem/export/changes",
        params={"since": "2026-01-01T00:00:00Z", "since_id": "0" * 26},
        headers=member,
    )
    assert r.status_code == 200
    assert "next_since_id" in r.json()["meta"]
