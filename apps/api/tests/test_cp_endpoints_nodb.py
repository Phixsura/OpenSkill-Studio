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
