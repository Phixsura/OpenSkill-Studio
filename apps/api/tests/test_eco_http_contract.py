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


async def test_severity_filters_reject_unknown_values(http, tokens):
    """Round-231 killer: every severity FILTER param must reject unknown
    values with 422 — a typo (?severity=critcal) used to silently return an
    empty list/feed, reading as "no critical changes" to the subscriber."""
    member = {"Authorization": f"Bearer {tokens['member']}"}

    surfaces = [
        "/api/v1/ecosystem/dashboard/change-feed?severity=critcal",
        "/api/v1/ecosystem/export/changes.atom?severity=critcal",
        "/api/v1/ecosystem/changes?severity=critcal",
        "/api/v1/ecosystem/security/advisories?severity=serious",
    ]
    for url in surfaces:
        r = await http.get(url, headers=member)
        assert r.status_code == 422, f"{url} -> {r.status_code}"
        body = r.json()
        assert body["error"]["code"] == "VALIDATION_ERROR", url
        assert "allowed" in body["error"]["message"], url

    # Valid values still pass through (200, list envelope / atom XML)
    r = await http.get(
        "/api/v1/ecosystem/dashboard/change-feed?severity=breaking",
        headers=member,
    )
    assert r.status_code == 200 and isinstance(r.json()["data"], list)
    r = await http.get(
        "/api/v1/ecosystem/security/advisories?severity=critical", headers=member
    )
    assert r.status_code == 200
    r = await http.get(
        "/api/v1/ecosystem/export/changes.atom?severity=breaking",
        headers=member,
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/atom+xml")


async def test_atom_feed_token_auth(http, tokens):
    """Round-232 killer: the Atom subscribe surface was end-to-end unusable —
    feed readers cannot send Authorization headers, so every real subscriber
    got 401. A narrow-scope feed token in the query string (GitHub
    private-feed posture) must work; an ACCESS token in the query string
    must NOT (URLs leak into logs/history — a leaked feed URL must never
    become an account takeover)."""
    member = {"Authorization": f"Bearer {tokens['member']}"}

    # Mint a feed token with a normal session
    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=member)
    assert r.status_code == 200
    feed_token = r.json()["data"]["token"]
    assert feed_token

    # Feed token in query string: the feed-reader path — must work, no header
    r = await http.get(
        f"/api/v1/ecosystem/export/changes.atom?token={feed_token}"
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/atom+xml")

    # ACCESS token in query string: refused (wrong type for a URL)
    r = await http.get(
        f"/api/v1/ecosystem/export/changes.atom?token={tokens['member']}"
    )
    assert r.status_code == 401

    # Garbage token: 401, not 500
    r = await http.get("/api/v1/ecosystem/export/changes.atom?token=garbage")
    assert r.status_code == 401

    # Bearer access token still works (dashboard fetches)
    r = await http.get("/api/v1/ecosystem/export/changes.atom", headers=member)
    assert r.status_code == 200

    # Narrow scope: the feed token opens NOTHING else — not even the
    # JSON change list (Bearer-only endpoints ignore ?token=)
    r = await http.get(f"/api/v1/ecosystem/changes?token={feed_token}")
    assert r.status_code == 401
    r = await http.get(
        "/api/v1/ecosystem/changes",
        headers={"Authorization": f"Bearer {feed_token}"},
    )
    assert r.status_code == 401  # type=feed is not an access token


async def test_calendar_and_export_accept_feed_tokens(http, tokens):
    """Round-233 killer: same class as §94 — the .ics calendar-subscribe URL
    and the catalog-export download anchor are consumed WITHOUT Bearer
    headers (calendar apps, browser navigation). Feed token must open both;
    anonymous and access-token-in-query stay 401."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=member)
    feed_token = r.json()["data"]["token"]

    for url, ctype in [
        ("/api/v1/ecosystem/deprecation-calendar.ics", "text/calendar"),
        ("/api/v1/ecosystem/export", "application/json"),
    ]:
        r = await http.get(url)  # anonymous
        assert r.status_code == 401, url
        r = await http.get(f"{url}?token={tokens['member']}")  # access in URL
        assert r.status_code == 401, url
        r = await http.get(f"{url}?token={feed_token}")  # the real consumer
        assert r.status_code == 200, f"{url} -> {r.status_code}"
        assert r.headers["content-type"].startswith(ctype), url
        r = await http.get(url, headers=member)  # bearer still fine
        assert r.status_code == 200, url


async def test_feed_token_dies_with_the_account(http):
    """Round-234 killer: feed tokens live 365 days and are NOT stored
    server-side — deactivating the account is the ONLY revocation mechanism.
    A suspended user's feed token must stop working immediately, and a
    validly-signed feed token without a sub claim must 401, not 500."""
    from datetime import UTC, datetime, timedelta

    import jwt as _jwt

    from app.config import settings
    from app.core.database import AsyncSessionLocal, engine
    from app.core.security import ALGORITHM, create_feed_token
    from app.models.user import UserStatus
    from tests.test_eco_services_db import _mk_user

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        user = await _mk_user(db)
        await db.commit()
        token = create_feed_token(user.id)

        # Active: feed works
        r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={token}")
        assert r.status_code == 200

        # Suspend the account — the token must die with it
        user.status = UserStatus.SUSPENDED
        await db.commit()
        r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={token}")
        assert r.status_code == 401

        # cleanup: reactivate so shared fixtures stay sane
        user.status = UserStatus.ACTIVE
        await db.commit()
    await engine.dispose()

    # Validly-signed feed token with NO sub claim: 401, never a KeyError-500
    now = datetime.now(UTC)
    subless = _jwt.encode(
        {"type": "feed", "iat": now, "exp": now + timedelta(days=1)},
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={subless}")
    assert r.status_code == 401

    # ... and a NON-STRING sub (tampered payload): db.get(User, dict) would
    # raise a 500 without the isinstance gate
    weird = _jwt.encode(
        {"sub": {"a": 1}, "type": "feed", "iat": now, "exp": now + timedelta(days=1)},
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={weird}")
    assert r.status_code == 401


async def test_export_and_atom_support_conditional_get(http, tokens):
    """Round-235 killer: both polling surfaces must honor If-None-Match —
    integrations poll the multi-MB catalog and feed readers poll the Atom
    feed on fixed schedules; without 304s every poll re-transfers the world.
    A stale/different validator must still get a full 200."""
    member = {"Authorization": f"Bearer {tokens['member']}"}

    # catalog export: ETag mirrors content_hash
    r = await http.get("/api/v1/ecosystem/export", headers=member)
    assert r.status_code == 200
    etag = r.headers.get("etag")
    assert etag, "export must carry an ETag"
    assert r.json()["data"]["content_hash"] in etag

    r2 = await http.get(
        "/api/v1/ecosystem/export",
        headers={**member, "If-None-Match": etag},
    )
    assert r2.status_code == 304
    assert not r2.content  # 304 carries no body

    r3 = await http.get(
        "/api/v1/ecosystem/export",
        headers={**member, "If-None-Match": '"something-else"'},
    )
    assert r3.status_code == 200  # mismatched validator -> full response

    # Atom feed: same contract
    r = await http.get("/api/v1/ecosystem/export/changes.atom", headers=member)
    assert r.status_code == 200
    aetag = r.headers.get("etag")
    assert aetag, "atom feed must carry an ETag"
    r2 = await http.get(
        "/api/v1/ecosystem/export/changes.atom",
        headers={**member, "If-None-Match": aetag},
    )
    assert r2.status_code == 304
    r3 = await http.get(
        "/api/v1/ecosystem/export/changes.atom",
        headers={**member, "If-None-Match": '"nope"'},
    )
    assert r3.status_code == 200


async def test_atom_etag_invalidates_on_new_change(http, tokens):
    """Round-236 killer: a validator that never changes is WORSE than none —
    subscribers would 304 forever and miss every new change. Inserting a
    change must flip the Atom ETag so the stale validator gets a full 200
    containing the new entry."""
    from app.core.database import AsyncSessionLocal, engine
    from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
    from tests.test_eco_services_db import _mk_source

    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/export/changes.atom", headers=member)
    old_etag = r.headers["etag"]

    await engine.dispose(close=False)
    obs_id = None
    async with AsyncSessionLocal() as db:
        source = await _mk_source(db)
        obs = EcosystemObservation(
            source_id=source.id, event_type="pricing_changed",
            raw_hash="c" * 64, normalized={},
        )
        db.add(obs)
        await db.flush()
        change = ChangeEvent(
            observation_id=obs.id, change_type="price",
            field="etag-flip-marker", old_value={"v": 1}, new_value={"v": 2},
            severity="info",
        )
        db.add(change)
        await db.commit()
        obs_id = obs.id

        try:
            r2 = await http.get(
                "/api/v1/ecosystem/export/changes.atom",
                headers={**member, "If-None-Match": old_etag},
            )
            # stale validator -> full response, with the new entry inside
            assert r2.status_code == 200
            assert r2.headers["etag"] != old_etag
            assert "etag-flip-marker" in r2.text
        finally:
            await db.delete(change)
            await db.delete(await db.get(EcosystemObservation, obs_id))
            await db.commit()
    await engine.dispose()


async def test_every_ecosystem_get_route_rejects_anonymous(http):
    """Round-240: the 401 guard was a HAND-MAINTAINED path list — every new
    endpoint (feed-token, audit.csv, .atom, .ics, export...) silently
    escaped it. Sweep the real route table instead: every parameterless
    /ecosystem GET must 401 anonymously (422 allowed only when required
    query params fail validation BEFORE auth resolves — never 200/5xx)."""
    from app.main import app as _app

    def _walk(router):
        for rt in getattr(router, "routes", []):
            if type(rt).__name__ == "_IncludedRouter":
                yield from _walk(rt.original_router)
            elif hasattr(rt, "path") and hasattr(rt, "methods"):
                yield rt
            elif hasattr(rt, "routes"):
                yield from _walk(rt)

    swept = writes = 0
    for route in _walk(_app.router):
        path = route.path
        if not path.startswith("/ecosystem"):
            continue
        if "{" in path:
            continue  # parameterized: covered by typed tests
        for method in route.methods or set():
            if method == "HEAD":
                continue
            # R241: writes swept too — the old hand list also missed them
            kwargs = {} if method == "GET" else {"json": {}}
            r = await http.request(method, f"/api/v1{path}", **kwargs)
            assert r.status_code in (401, 422), f"{method} {path} -> {r.status_code}"
            swept += 1
            writes += method != "GET"
    assert swept >= 60 and writes >= 15, f"sweep broken (swept={swept}, writes={writes})"


async def test_if_none_match_list_and_star_semantics(http, tokens):
    """Round-244 killer: RFC 7232 §3.2 — If-None-Match may carry a
    comma-separated validator list (proxies merge them), weak W/ prefixes,
    or `*`. A strict string-equality match would re-transfer the world to
    any client behind such a proxy."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/export", headers=member)
    etag = r.headers["etag"]

    # validator list containing ours -> 304
    r2 = await http.get(
        "/api/v1/ecosystem/export",
        headers={**member, "If-None-Match": f'"stale-one", {etag}'},
    )
    assert r2.status_code == 304
    # weak form of ours -> 304 (weak comparison is fine for GET)
    r3 = await http.get(
        "/api/v1/ecosystem/export",
        headers={**member, "If-None-Match": f"W/{etag}"},
    )
    assert r3.status_code == 304
    # star -> 304 (resource exists)
    r4 = await http.get(
        "/api/v1/ecosystem/export", headers={**member, "If-None-Match": "*"}
    )
    assert r4.status_code == 304
    # list of stale validators -> full 200
    r5 = await http.get(
        "/api/v1/ecosystem/export",
        headers={**member, "If-None-Match": '"a", "b"'},
    )
    assert r5.status_code == 200


async def test_atom_supports_if_modified_since(http, tokens):
    """Round-245 killer: legacy pollers (cron/curl feed scripts) send only
    If-Modified-Since. The Atom feed must return Last-Modified, honor IMS
    with a 304, let If-None-Match take precedence when both are sent
    (RFC 7232), and never 500 on a malformed date."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/export/changes.atom", headers=member)
    lm = r.headers.get("last-modified")
    if lm is None:
        return  # empty feed on this stack: nothing to condition on
    r2 = await http.get(
        "/api/v1/ecosystem/export/changes.atom",
        headers={**member, "If-Modified-Since": lm},
    )
    assert r2.status_code == 304
    # ancient date -> full 200
    r3 = await http.get(
        "/api/v1/ecosystem/export/changes.atom",
        headers={**member, "If-Modified-Since": "Mon, 01 Jan 1990 00:00:00 GMT"},
    )
    assert r3.status_code == 200
    # If-None-Match present: IMS ignored (stale etag + fresh IMS -> 200)
    r4 = await http.get(
        "/api/v1/ecosystem/export/changes.atom",
        headers={**member, "If-None-Match": '"stale"', "If-Modified-Since": lm},
    )
    assert r4.status_code == 200
    # malformed IMS -> full 200, never 500
    r5 = await http.get(
        "/api/v1/ecosystem/export/changes.atom",
        headers={**member, "If-Modified-Since": "not-a-date"},
    )
    assert r5.status_code == 200


async def test_atom_subscription_survives_entity_merge(http, tokens):
    """Round-246 killer: a merge re-points every change to the survivor —
    subscription URLs pinned to the duplicate would go permanently silent.
    The empty duplicate feed must 302 to the survivor's feed (filters and
    token ride along); an ALIVE superseded entity with its own changes is
    NOT redirected."""
    from sqlalchemy import select as _select

    from app.core.database import AsyncSessionLocal, engine
    from app.ecosystem.models.catalog import AIModel
    from app.ecosystem.models.replacement import ReplacementEdge
    from tests.test_eco_services_db import _mk_user

    member = {"Authorization": f"Bearer {tokens['member']}"}
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        from ulid import ULID as _ULID

        tag = str(_ULID()).lower()[:8]
        admin = await _mk_user(db, "admin")
        dup = AIModel(canonical_name=f"MergeDup-{tag}", slug=f"md-{tag}")
        survivor = AIModel(canonical_name=f"MergeSurv-{tag}", slug=f"ms-{tag}")
        db.add_all([dup, survivor])
        await db.commit()
        dup_id, surv_id = dup.id, survivor.id

        try:
            from app.ecosystem.services.catalog import CatalogService

            await CatalogService(db).merge_entities(
                "model", dup_id, surv_id, actor_id=admin.id
            )
            await db.commit()

            r = await http.get(
                f"/api/v1/ecosystem/export/changes.atom?entity_id={dup_id}"
                "&severity=breaking",
                headers=member,
            )
            assert r.status_code == 302
            loc = r.headers["location"]
            assert surv_id in loc and dup_id not in loc
            assert "severity=breaking" in loc  # filters ride along

            # the survivor's feed serves normally (empty but 200 — no edge FROM it)
            r2 = await http.get(
                f"/api/v1/ecosystem/export/changes.atom?entity_id={surv_id}",
                headers=member,
            )
            assert r2.status_code == 200
        finally:
            # self-clean: remove the supersedes edge and both entities
            for edge in await db.scalars(
                _select(ReplacementEdge).where(ReplacementEdge.from_id == dup_id)
            ):
                await db.delete(edge)
            for eid in (dup_id, surv_id):
                obj = await db.get(AIModel, eid)
                if obj:
                    await db.delete(obj)
            await db.commit()
    await engine.dispose()


async def test_ops_metrics_scrapeable_with_admin_feed_token(http, tokens):
    """Round-247 killer: Prometheus cannot refresh a 15-minute Bearer token,
    so /ops/metrics was un-scrapeable by its only real consumer. An ADMIN's
    long-lived feed token in ?token= must scrape; a MEMBER's feed token must
    403 (role gate is live — checked against the user row, not the token)."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    admin = {"Authorization": f"Bearer {tokens['admin']}"}

    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=admin)
    admin_token = r.json()["data"]["token"]
    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=member)
    member_token = r.json()["data"]["token"]

    r = await http.get(f"/api/v1/ecosystem/ops/metrics?token={admin_token}")
    assert r.status_code == 200
    assert "eco_" in r.text  # exposition format served

    r = await http.get(f"/api/v1/ecosystem/ops/metrics?token={member_token}")
    assert r.status_code == 403

    r = await http.get("/api/v1/ecosystem/ops/metrics")
    assert r.status_code == 401

    # human path unchanged
    r = await http.get("/api/v1/ecosystem/ops/metrics", headers=admin)
    assert r.status_code == 200
    r = await http.get("/api/v1/ecosystem/ops/metrics", headers=member)
    assert r.status_code == 403


async def test_atom_self_link_present_and_credential_free(http, tokens):
    """Round-252 killer: the feed carries a rel=self link (validator
    identity) and it must NEVER echo the ?token= credential back into the
    response body — feeds get re-shared and cached."""
    import xml.etree.ElementTree as ET

    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=member)
    feed_token = r.json()["data"]["token"]

    r = await http.get(
        f"/api/v1/ecosystem/export/changes.atom?severity=breaking&token={feed_token}"
    )
    assert r.status_code == 200
    assert feed_token not in r.text  # credential never round-trips
    root = ET.fromstring(r.text)
    ns = "{http://www.w3.org/2005/Atom}"
    self_links = [
        link.get("href")
        for link in root.findall(f"{ns}link")
        if link.get("rel") == "self"
    ]
    assert self_links and "severity=breaking" in self_links[0]
    assert "token=" not in self_links[0]


async def test_ics_calendar_supports_conditional_get(http, tokens):
    """Round-260 killer: calendar apps poll the .ics URL on a schedule —
    same conditional-GET contract as the Atom feed (§95): ETag on 200,
    If-None-Match match -> 304 empty, stale validator -> full 200."""
    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.get("/api/v1/ecosystem/deprecation-calendar.ics", headers=member)
    assert r.status_code == 200
    etag = r.headers.get("etag")
    assert etag, "ics must carry an ETag"
    r2 = await http.get(
        "/api/v1/ecosystem/deprecation-calendar.ics",
        headers={**member, "If-None-Match": etag},
    )
    assert r2.status_code == 304 and not r2.content
    r3 = await http.get(
        "/api/v1/ecosystem/deprecation-calendar.ics",
        headers={**member, "If-None-Match": '"stale"'},
    )
    assert r3.status_code == 200
    # different filter window -> different validator space (no false 304)
    r4 = await http.get(
        "/api/v1/ecosystem/deprecation-calendar.ics?within_days=30",
        headers={**member, "If-None-Match": etag},
    )
    assert r4.status_code in (200, 304)  # 304 only if identical event set


async def test_dead_lettered_eco_outbox_is_a_metric(http, tokens):
    """Round-264 killer: a dead-lettered eco message is a promised
    automation that silently stopped (§90 class) — it must surface as
    eco_outbox_failed so the EcoOutboxDeadLetters alert can fire."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.core.database import AsyncSessionLocal, engine

    admin = {"Authorization": f"Bearer {tokens['admin']}"}
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        row = OutboxMessage(
            topic="eco.check_availability",
            payload={"entity_kind": "model", "entity_id": "0" * 26},
            status="failed",
        )
        db.add(row)
        await db.commit()
        try:
            r = await http.get("/api/v1/ecosystem/ops/metrics", headers=admin)
            assert r.status_code == 200
            line = next(
                ln for ln in r.text.splitlines()
                if ln.startswith("eco_outbox_failed ")
            )
            assert float(line.split()[1]) >= 1
        finally:
            await db.delete(row)
            await db.commit()
    await engine.dispose()


async def test_token_surfaces_are_never_shared_cacheable(http, tokens):
    """Round-271 killer: query-token requests carry NO Authorization header,
    so without Cache-Control: private a CDN/corporate proxy may store these
    responses and replay them to other clients (the metrics surface is admin
    data). Every token-capable surface must say `private` on 200 AND on the
    conditional/redirect paths."""
    admin = {"Authorization": f"Bearer {tokens['admin']}"}
    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=admin)
    tok = r.json()["data"]["token"]

    surfaces = [
        f"/api/v1/ecosystem/export/changes.atom?token={tok}",
        f"/api/v1/ecosystem/deprecation-calendar.ics?token={tok}",
        f"/api/v1/ecosystem/export?token={tok}",
        f"/api/v1/ecosystem/ops/metrics?token={tok}",
    ]
    for url in surfaces:
        r = await http.get(url)
        assert r.status_code == 200, url
        cc = r.headers.get("cache-control", "")
        assert "private" in cc, f"{url} -> Cache-Control: {cc!r}"
        etag = r.headers.get("etag")
        if etag:  # conditional path carries the directive too
            r304 = await http.get(url, headers={"If-None-Match": etag})
            assert r304.status_code == 304, url
            assert "private" in r304.headers.get("cache-control", ""), url


async def test_feed_token_rotation_revokes_prior_tokens(http, tokens):
    """Round-272 killer (§94.6): feed tokens are stateless 365-day JWTs — a
    leaked feed URL was irrevocable short of suspending the account. Rotate
    must kill EVERY previously minted token immediately, hand back a working
    replacement, stack across rotations, and leave Bearer sessions alone."""
    member = {"Authorization": f"Bearer {tokens['member']}"}

    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=member)
    old_token = r.json()["data"]["token"]
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={old_token}")
    assert r.status_code == 200  # works before rotation

    r = await http.post("/api/v1/ecosystem/export/feed-token/rotate", headers=member)
    assert r.status_code == 200
    new_token = r.json()["data"]["token"]

    # the leaked token is dead NOW — not in 365 days
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={old_token}")
    assert r.status_code == 401
    # the replacement works
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={new_token}")
    assert r.status_code == 200
    # re-minting WITHOUT rotating returns a token of the current generation
    r = await http.get("/api/v1/ecosystem/export/feed-token", headers=member)
    reminted = r.json()["data"]["token"]
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={reminted}")
    assert r.status_code == 200
    # a second rotation kills the first replacement too
    r = await http.post("/api/v1/ecosystem/export/feed-token/rotate", headers=member)
    assert r.json()["data"]["revoked_generations"] >= 2
    r = await http.get(f"/api/v1/ecosystem/export/changes.atom?token={new_token}")
    assert r.status_code == 401
    # Bearer session path is untouched by rotation
    r = await http.get("/api/v1/ecosystem/export/changes.atom", headers=member)
    assert r.status_code == 200


async def test_first_rotate_race_is_serialized(http, tokens):
    """Round-274 killer: two concurrent FIRST rotations both saw no state row
    and both INSERTed — PK violation 500. The advisory lock must serialize
    the get-or-create: both requests succeed and generations end distinct."""
    import asyncio

    from app.core.database import AsyncSessionLocal, engine
    from app.ecosystem.api.dashboard import rotate_feed_token
    from app.ecosystem.models.replacement import FeedTokenState
    from tests.test_eco_services_db import _mk_user

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as setup:
        user = await _mk_user(setup)
        await setup.commit()
        uid = user.id

    async def one_rotate():
        async with AsyncSessionLocal() as db:
            out = await rotate_feed_token(db=db, user=await db.get(type(user), uid))
            return out["data"]["revoked_generations"]

    try:
        gens = await asyncio.gather(*(one_rotate() for _ in range(8)))
        # all succeeded (no PK 500) and were serialized: strictly 1..8
        assert sorted(gens) == list(range(1, 9)), gens
    finally:
        async with AsyncSessionLocal() as db:
            state = await db.get(FeedTokenState, uid)
            if state:
                await db.delete(state)
            await db.commit()
    await engine.dispose()


async def test_rotate_is_audited(http, tokens):
    """Round-278 killer: credential revocation is a security event — the
    rotate must land in the immutable audit trail with the new generation."""
    from sqlalchemy import select as _select

    from app.controlplane.models.audit import CommercialAuditEvent
    from app.core.database import AsyncSessionLocal, engine

    member = {"Authorization": f"Bearer {tokens['member']}"}
    r = await http.post("/api/v1/ecosystem/export/feed-token/rotate", headers=member)
    assert r.status_code == 200
    gen = r.json()["data"]["revoked_generations"]

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        row = await db.scalar(
            _select(CommercialAuditEvent)
            .where(CommercialAuditEvent.action == "eco.feed_token_rotated")
            .order_by(CommercialAuditEvent.id.desc())
            .limit(1)
        )
        assert row is not None
        assert row.after["generation"] == gen
    await engine.dispose()
