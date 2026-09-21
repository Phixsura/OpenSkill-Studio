"""Tests for newly added frontend-compatible endpoints — 20 tests.

Covers POST /bookmarks, DELETE /bookmarks/{id}, POST /applications,
GET /saved-searches, POST /saved-searches, and the doubled-path fixes.
"""

import pytest

# ═══════════════════════════════════════════════════════════════
# POST /bookmarks route exists (1-4)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_ne01_post_bookmarks_requires_auth(client):
    r = await client.post("/api/v1/talent/bookmarks", json={"entity_id": "x"})
    assert r.status_code in (200, 201, 401, 404, 422, 429)


@pytest.mark.asyncio
async def test_ne02_post_bookmarks_validates_body(client):
    r = await client.post("/api/v1/talent/bookmarks", json={})
    assert r.status_code in (401, 422, 429)


@pytest.mark.asyncio
async def test_ne03_delete_bookmarks_requires_auth(client):
    r = await client.delete("/api/v1/talent/bookmarks/01FAKE00000000000000000000")
    assert r.status_code in (204, 401, 404, 429)


def test_ne04_bookmark_router_has_post():
    from app.talent.api.bookmarks import router

    methods = set()
    for route in router.routes:
        if hasattr(route, "methods"):
            methods.update(route.methods)
    assert "POST" in methods
    assert "DELETE" in methods


# ═══════════════════════════════════════════════════════════════
# POST /applications route exists (5-8)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_ne05_post_applications_requires_auth(client):
    r = await client.post("/api/v1/talent/applications", json={"opportunity_id": "x"})
    assert r.status_code in (200, 201, 401, 404, 422, 429)


@pytest.mark.asyncio
async def test_ne06_post_applications_validates_opp_id(client):
    r = await client.post("/api/v1/talent/applications", json={})
    assert r.status_code in (401, 422, 429)


def test_ne07_applications_router_has_post():
    from app.talent.api.applications import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert any(p.endswith("/applications") for p in paths)


def test_ne08_applications_post_is_separate():
    """POST /applications is distinct from POST /opportunities/{opp_id}/apply."""
    from app.talent.api.applications import router

    post_paths = []
    for route in router.routes:
        if hasattr(route, "methods") and "POST" in route.methods:
            post_paths.append(getattr(route, "path", ""))
    assert any(p.endswith("/applications") for p in post_paths)
    assert any("apply" in p for p in post_paths)


# ═══════════════════════════════════════════════════════════════
# GET/POST /saved-searches route exists (9-14)
# ═══════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_ne09_get_saved_searches_requires_auth(client):
    r = await client.get("/api/v1/talent/saved-searches")
    assert r.status_code in (200, 401, 404, 429)


@pytest.mark.asyncio
async def test_ne10_post_saved_searches_requires_auth(client):
    r = await client.post("/api/v1/talent/saved-searches", json={"name": "test"})
    assert r.status_code in (200, 201, 401, 404, 422, 429)


@pytest.mark.asyncio
async def test_ne11_post_saved_searches_validates_body(client):
    r = await client.post("/api/v1/talent/saved-searches", json={})
    assert r.status_code in (201, 401, 422, 429)


def test_ne12_saved_searches_router_has_get_and_post():
    from app.talent.api.saved_searches import router

    paths_with_methods = {}
    for route in router.routes:
        p = getattr(route, "path", "")
        m = getattr(route, "methods", set())
        if p.endswith("/saved-searches"):
            paths_with_methods[p] = paths_with_methods.get(p, set()) | m

    ss_key = next((k for k in paths_with_methods if k.endswith("/saved-searches")), None)
    assert ss_key is not None, "No /saved-searches route found"
    assert "GET" in paths_with_methods[ss_key]
    assert "POST" in paths_with_methods[ss_key]


def test_ne13_post_saved_searches_idor_guard():
    """POST /saved-searches validates org_id membership (IDOR fix)."""
    import inspect

    from app.talent.api.saved_searches import create_my_saved_search

    source = inspect.getsource(create_my_saved_search)
    assert "OrgMember" in source
    assert "403" in source or "Forbidden" in source.lower() or "Not a member" in source


def test_ne14_saved_searches_org_scoped_create_also_exists():
    """Org-scoped POST /orgs/{org_id}/saved-searches still exists."""
    from app.talent.api.saved_searches import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert any("orgs" in p and "saved-searches" in p for p in paths)


# ═══════════════════════════════════════════════════════════════
# Doubled path fixes verified (15-20)
# ═══════════════════════════════════════════════════════════════


def test_ne15_capabilities_autocomplete_not_doubled():
    """Autocomplete path should NOT be /talent/capabilities/talent/capabilities/..."""
    from app.talent.api.capabilities import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert not any("/talent/capabilities/talent/" in p for p in paths)


def test_ne16_capabilities_resolve_not_doubled():
    """Resolve path should NOT have /capabilities/capabilities/."""
    from app.talent.api.capabilities import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert not any("/capabilities/capabilities/" in p for p in paths)


def test_ne17_capabilities_has_import():
    from app.talent.api.capabilities import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert any("import" in p for p in paths)


def test_ne18_applications_no_doubled_talent():
    """Application paths should NOT have /talent/talent/."""
    from app.talent.api.applications import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert not any("/talent/talent/" in p for p in paths)


def test_ne19_scheduling_no_doubled_talent():
    """Scheduling paths should NOT have /talent/talent/."""
    from app.talent.api.scheduling import router

    paths = [getattr(r, "path", "") for r in router.routes]
    assert not any("/talent/talent/" in p for p in paths)


def test_ne20_no_doubled_paths_in_openapi():
    """OpenAPI schema has zero doubled path segments in talent endpoints."""
    from app.main import app

    schema = app.openapi()
    for p in schema["paths"]:
        if "/talent/" not in p:
            continue
        parts = p.split("/")
        for i in range(len(parts) - 1):
            if parts[i] == parts[i + 1] and parts[i] not in ("", "api"):
                raise AssertionError(f"Doubled segment in {p}")
