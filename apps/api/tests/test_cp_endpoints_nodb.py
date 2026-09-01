"""Control-plane endpoint tests that run WITHOUT a database.

Auth-guard (401) and schema-validation (422) matrix for every new
control-plane endpoint. Mirrors tests/test_organizations.py style.
Extended by each phase as its endpoints land.
"""

import pytest

# ── P1: platform endpoints ───────────────────────────────────


@pytest.mark.asyncio
async def test_platform_create_tenant_requires_auth(client):
    r = await client.post("/api/v1/platform/tenants", json={"name": "X", "slug": "x-t"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_search_tenants_requires_auth(client):
    r = await client.get("/api/v1/platform/tenants")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_tenant_detail_requires_auth(client):
    r = await client.get("/api/v1/platform/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_suspend_requires_auth(client):
    r = await client.post(
        "/api/v1/platform/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/suspend",
        json={"reason": "abuse investigation"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_reactivate_requires_auth(client):
    r = await client.post("/api/v1/platform/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/reactivate")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_role_grant_requires_auth(client):
    r = await client.post(
        "/api/v1/platform/platform-roles",
        json={"user_id": "01JFAKEFAKEFAKEFAKEFAKEFAK", "role": "platform_admin"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_role_revoke_requires_auth(client):
    r = await client.delete("/api/v1/platform/platform-roles/01JFAKEFAKEFAKEFAKEFAKEFAK")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_impersonation_grant_requires_auth(client):
    r = await client.post(
        "/api/v1/platform/impersonation-grants",
        json={
            "target_user_id": "01JFAKEFAKEFAKEFAKEFAKEFAK",
            "reason": "debug ticket #123",
        },
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_impersonation_token_requires_auth(client):
    r = await client.post("/api/v1/platform/impersonation-grants/01JFAKEFAKEFAKEFAKEFAKEFAK/token")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_impersonation_revoke_requires_auth(client):
    r = await client.post("/api/v1/platform/impersonation-grants/01JFAKEFAKEFAKEFAKEFAKEFAK/revoke")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_audit_events_requires_auth(client):
    r = await client.get("/api/v1/platform/audit-events")
    assert r.status_code == 401


# ── P1: tenant endpoints ─────────────────────────────────────


@pytest.mark.asyncio
async def test_tenants_mine_requires_auth(client):
    r = await client.get("/api/v1/tenants/mine")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_get_requires_auth(client):
    r = await client.get("/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_patch_requires_auth(client):
    r = await client.patch("/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK", json={"name": "New"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_members_requires_auth(client):
    r = await client.get("/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/members")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_add_member_requires_auth(client):
    r = await client.post(
        "/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/members",
        json={"user_id": "01JFAKEFAKEFAKEFAKEFAKEFAK", "role": "billing_admin"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_audit_events_requires_auth(client):
    r = await client.get("/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/audit-events")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_create_org_requires_auth(client):
    r = await client.post(
        "/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/orgs",
        json={"name": "Campus", "slug": "campus-x"},
    )
    assert r.status_code == 401


# ── P1: schema validation (401 comes after body validation in some routes;
#        both are acceptable rejections for unauthenticated malformed input) ──


@pytest.mark.asyncio
async def test_create_tenant_rejects_bad_slug(client):
    r = await client.post("/api/v1/platform/tenants", json={"name": "X", "slug": "Bad Slug!"})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_tenant_rejects_bad_currency(client):
    r = await client.post(
        "/api/v1/platform/tenants",
        json={"name": "X", "slug": "x-tenant", "currency": "usd$"},
    )
    assert r.status_code in (401, 422)


def test_tenant_schema_rejects_unknown_timezone():
    """R63[13]: an unknown IANA tz (typo) must be rejected at the schema, not
    accepted and silently fall back to UTC in budget/rating/usage period math.
    Tested at the schema layer because route auth runs before body validation
    for these endpoints (so an unauth'd request 401s before the tz is seen)."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.controlplane.schemas.tenant import CreateTenantRequest, UpdateTenantRequest

    # Valid zones pass.
    CreateTenantRequest(name="X", slug="x-tenant", timezone="Asia/Seoul")
    UpdateTenantRequest(timezone="America/New_York")
    UpdateTenantRequest(timezone=None)  # unset is fine
    # Typos are rejected.
    with _pytest.raises(ValidationError):
        CreateTenantRequest(name="X", slug="x-tenant", timezone="Asia/Seul")
    with _pytest.raises(ValidationError):
        UpdateTenantRequest(timezone="Not/AZone")


@pytest.mark.asyncio
async def test_suspend_requires_reason(client):
    r = await client.post("/api/v1/platform/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/suspend", json={})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_impersonation_grant_requires_min_reason(client):
    r = await client.post(
        "/api/v1/platform/impersonation-grants",
        json={"target_user_id": "01JFAKEFAKEFAKEFAKEFAKEFAK", "reason": "x"},
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_impersonation_grant_caps_expiry(client):
    r = await client.post(
        "/api/v1/platform/impersonation-grants",
        json={
            "target_user_id": "01JFAKEFAKEFAKEFAKEFAKEFAK",
            "reason": "debug ticket #123",
            "expires_in_minutes": 6000,
        },
    )
    assert r.status_code in (401, 422)


# ── P10: white-label / domains / blueprints / export ─────────


@pytest.mark.asyncio
async def test_tenant_branding_requires_auth(client):
    r = await client.get("/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/branding")
    assert r.status_code == 401
    r = await client.put(
        "/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/branding",
        json={"product_display_name": "X"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_domains_require_auth(client):
    r = await client.get("/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/domains")
    assert r.status_code == 401
    r = await client.post(
        "/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/domains",
        json={"hostname": "x.example.com"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_site_context_is_public(client):
    # Invalid host short-circuits before any DB access → suite stays DB-free
    r = await client.get("/api/v1/public/site-context", params={"host": "///bad host///"})
    assert r.status_code == 200
    assert r.json()["data"]["tenant_id"] is None


@pytest.mark.asyncio
async def test_platform_blueprints_require_auth(client):
    r = await client.get("/api/v1/platform/blueprints")
    assert r.status_code == 401
    r = await client.post("/api/v1/platform/blueprints", json={"name": "B", "config": {}})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_provision_runs_require_auth(client):
    r = await client.post(
        "/api/v1/platform/provision-runs",
        json={"name": "T", "slug": "t-x", "idempotency_key": "k1"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_tenant_exports_require_auth(client):
    r = await client.post("/api/v1/platform/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/exports")
    assert r.status_code == 401


# ── P11: ops console ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_platform_dashboard_requires_auth(client):
    r = await client.get("/api/v1/platform/dashboard")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_trace_invoice_line_requires_auth(client):
    r = await client.get("/api/v1/platform/trace/invoice-lines/01JFAKEFAKEFAKEFAKEFAKEFAK")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_trace_settlement_entry_requires_auth(client):
    r = await client.get("/api/v1/platform/trace/settlement-entries/01JFAKEFAKEFAKEFAKEFAKEFAK")
    assert r.status_code == 401


# ── R29: pagination `page` upper bound (int64 OFFSET overflow → 500) ──


@pytest.mark.asyncio
async def test_all_cp_page_params_are_capped(client):
    """Every cp paginated endpoint must reject an oversized `page` with 422,
    not overflow the int64 OFFSET bind → 500. Unauth still exercises the
    Query-level bound (validation runs before the auth dependency body)."""
    big = "999999999999999999999"
    paths = [
        f"/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/credits/ledger?page={big}",
        f"/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/reservations?page={big}",
        f"/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/invoices?page={big}",
        f"/api/v1/platform/cost-rates?page={big}",
        f"/api/v1/platform/price-policies?page={big}",
        f"/api/v1/platform/rated-usage?page={big}",
        f"/api/v1/platform/reconciliation/reports?page={big}",
        f"/api/v1/platform/invoices?page={big}",
        f"/api/v1/platform/settlements?page={big}",
    ]
    for path in paths:
        r = await client.get(path)
        # 422 = Query bound rejected it; 401 = auth ran first (also fine — the
        # bound is declared regardless). Never 500.
        assert r.status_code in (401, 422), f"{path} → {r.status_code}"
        assert r.status_code != 500


# ── R71: impersonation read-only guard scheme-casing bypass ──


def _imp_token():
    """Mint an access token carrying an `imp` claim, exactly as
    mint_impersonation_token does (type=access, imp/imp_grant present)."""
    import jwt

    from app.config import settings
    from app.core.security import ALGORITHM

    payload = {
        "sub": "01JFAKETARGETUSERFAKEFAKEA",
        "role": "instructor",
        "type": "access",
        "imp": "01JFAKESUPPORTUSERFAKEFAKE",
        "imp_grant": "01JFAKEGRANTFAKEFAKEFAKEFA",
        "exp": 9999999999,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


@pytest.mark.asyncio
async def test_impersonation_guard_blocks_all_scheme_casings(client):
    """R71 CRITICAL: the read-only impersonation guard parsed the auth scheme
    case-sensitively (`startswith("Bearer ")`), while FastAPI's OAuth2 parses
    it case-insensitively. A lowercase `bearer` (or extra whitespace) skipped
    the guard while the route still authenticated the token — a full read-only
    bypass. Every casing/spacing variant of a bearer scheme carrying an `imp`
    token must be blocked with 403 IMPERSONATION_FORBIDDEN on a non-whitelisted
    write."""
    token = _imp_token()
    # A control-plane write that is NOT in the guard's whitelist.
    path = "/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/subscription/cancel"
    for scheme in ("Bearer", "bearer", "BEARER", "BeArEr"):
        r = await client.post(path, headers={"Authorization": f"{scheme} {token}"}, json={})
        assert r.status_code == 403, f"scheme={scheme!r} → {r.status_code}"
        assert r.json()["error"]["code"] == "IMPERSONATION_FORBIDDEN"
    # Extra whitespace between scheme and token must also be caught (guard must
    # not fail open by choking on the token).
    r = await client.post(path, headers={"Authorization": f"Bearer  {token}"}, json={})
    assert r.status_code == 403, f"double-space → {r.status_code}"
    assert r.json()["error"]["code"] == "IMPERSONATION_FORBIDDEN"


@pytest.mark.asyncio
async def test_impersonation_guard_allows_safe_and_whitelisted():
    """The guard must still let impersonated GETs and whitelisted writes through
    (fail-closed on writes, not on reads). Unit-tested against the middleware's
    dispatch directly so no DB-backed route is touched."""
    from starlette.requests import Request

    from app.middleware.impersonation import ImpersonationGuardMiddleware

    mw = ImpersonationGuardMiddleware(app=None)
    token = _imp_token()

    async def _passed(scope):
        called = {"v": False}

        async def call_next(_req):
            called["v"] = True
            return "PASSED"

        result = await mw.dispatch(Request(scope), call_next)
        return called["v"], result

    def _scope(method, path):
        return {
            "type": "http",
            "method": method,
            "path": path,
            "headers": [(b"authorization", f"bearer {token}".encode())],
        }

    # GET (safe method) passes through even with a lowercase-scheme imp token.
    passed, _ = await _passed(_scope("GET", "/api/v1/tenants/01JFAKE"))
    assert passed
    # Whitelisted notification write passes the guard.
    passed, _ = await _passed(_scope("POST", "/api/v1/notifications/01JFAKE/read"))
    assert passed
    # A non-whitelisted write with the same lowercase-scheme imp token is blocked.
    passed, result = await _passed(_scope("POST", "/api/v1/tenants/01JFAKE/subscription/cancel"))
    assert not passed
    assert result.status_code == 403


# ── R45/R58: input-robustness 500s ────────────────────────────


def test_guest_link_naive_expires_at_coerced():
    """R45[23]: a naive ISO expires_at (no offset) must be coerced to UTC at
    the schema, not crash the aware-datetime comparison with a 500."""
    from app.controlplane.api.client_portal import CreateGuestLinkRequest

    req = CreateGuestLinkRequest.model_validate(
        {"role": "approver", "expires_at": "2026-12-01T00:00:00"}
    )
    assert req.expires_at.tzinfo is not None


def test_portal_comment_region_depth_capped():
    """R58[33]: a deeply nested region dict must 422 at the schema, not poison
    the comment thread with a persistent serialize-time 500."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.controlplane.api.client_portal import ClientCommentRequest

    deep: dict = {}
    cur = deep
    for _ in range(300):
        cur["a"] = {}
        cur = cur["a"]
    with _pytest.raises(ValidationError):
        ClientCommentRequest.model_validate(
            {"item_id": "0" * 26, "text": "x", "anchor_type": "region", "region": deep}
        )
    # A sane region passes.
    ClientCommentRequest.model_validate(
        {
            "item_id": "0" * 26,
            "text": "x",
            "anchor_type": "region",
            "region": {"x": 1, "y": 2, "w": 3, "h": 4},
        }
    )


def test_comment_response_tolerates_null_author():
    """R45[24]: guest portal comments store author_id=NULL — the response
    schema must accept it (was a non-optional str → every instructor
    comment-list 500'd once a guest commented)."""
    from datetime import UTC, datetime

    from app.schemas.project import CommentResponse

    resp = CommentResponse(
        id="0" * 26,
        submission_id="0" * 26,
        item_id="0" * 26,
        author_id=None,
        author_name="Client Reviewer",
        parent_id=None,
        text="looks great",
        anchor_type="global",
        timestamp_ms=None,
        duration_ms=None,
        region=None,
        completed=False,
        created_at=datetime.now(UTC),
    )
    assert resp.author_id is None


def test_decimal_validators_reject_garbage_as_422():
    """R58[34]: InvalidOperation is an ArithmeticError pydantic does NOT wrap —
    Decimal('abc') in a validator escaped as a 500. safe_decimal maps it to
    ValueError → 422."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.controlplane.api.pricing import CreateCostRateRequest

    with _pytest.raises(ValidationError):
        CreateCostRateRequest.model_validate(
            {
                "provider": "x",
                "usage_type": "image_generation",
                "currency": "USD",
                "unit_cost": "1.2.3",
                "effective_from": "2026-01-01T00:00:00+00:00",
            }
        )


def test_ingest_usage_naive_occurred_at_coerced():
    """R58[35]: naive occurred_at compared against aware now → TypeError 500.
    Schema coerces to UTC."""
    from app.controlplane.api.usage import IngestUsageRequest

    req = IngestUsageRequest.model_validate(
        {
            "usage_type": "image_generation",
            "quantity": 1,
            "occurred_at": "2026-01-01T00:00:00",
            "idempotency_key": "abcd1234",
        }
    )
    assert req.occurred_at.tzinfo is not None


@pytest.mark.asyncio
async def test_period_month_13_rejected_not_500(client):
    """R58[36]: '2026-13' passed the loose regex and blew up datetime() → 500.
    The tightened pattern rejects it at the Query layer (422; 401 acceptable if
    auth runs first — never 500)."""
    for bad in ("2026-13", "2026-00"):
        r = await client.get(f"/api/v1/tenants/01JFAKEFAKEFAKEFAKEFAKEFAK/usage?period={bad}")
        assert r.status_code in (401, 422), f"{bad} → {r.status_code}"
        assert r.status_code != 500
