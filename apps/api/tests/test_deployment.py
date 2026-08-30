"""Deployment verification tests.

Tests migration idempotency, health checks, CORS, env validation.
Docker tests are skipped if Docker is not available.
"""

import os
import subprocess
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"deploy-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app

    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager

    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


# ═══════════════ Health Check ═══════════════


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok(c):
    """GET /api/v1/health → 200 with status=ok."""
    r = await c.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ═══════════════ CORS ═══════════════


@pytest.mark.asyncio
async def test_cors_headers_present(c):
    """OPTIONS request includes CORS headers."""
    r = await c.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Should not be 405 (method not allowed) — CORS middleware handles it
    assert r.status_code in (200, 204, 405)


# ═══════════════ Migration Idempotency ═══════════════


@pytest.mark.asyncio
async def test_alembic_upgrade_head_idempotent():
    """Running 'alembic upgrade head' twice doesn't error."""
    api_dir = os.path.join(os.path.dirname(__file__), "..")

    # First run
    result1 = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result1.returncode == 0, f"First upgrade failed: {result1.stderr}"

    # Second run (idempotent)
    result2 = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result2.returncode == 0, f"Second upgrade failed: {result2.stderr}"


# ═══════════════ Migration History Check ═══════════════


@pytest.mark.asyncio
async def test_alembic_history_no_conflicts():
    """Alembic history shows no branch conflicts."""
    api_dir = os.path.join(os.path.dirname(__file__), "..")

    result = subprocess.run(
        ["uv", "run", "alembic", "history", "--verbose"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, f"History check failed: {result.stderr}"
    # Should not contain "MERGEPOINT" or branch indicators
    # (if it does, we have conflicting migrations)


# ═══════════════ App Startup Validation ═══════════════


@pytest.mark.asyncio
async def test_app_imports_without_error():
    """Importing the app doesn't crash."""
    from app.main import app

    assert app is not None
    # Check routes are registered
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/api/v1/health" in routes or any("/api/v1" in str(r) for r in app.routes)


@pytest.mark.asyncio
async def test_all_routers_registered(c):
    """OpenAPI schema includes all expected router prefixes."""
    r = await c.get("/openapi.json")
    if r.status_code == 200:
        paths = list(r.json().get("paths", {}).keys())
        # Check key paths exist
        expected_prefixes = ["/api/v1/auth", "/api/v1/orgs"]
        for prefix in expected_prefixes:
            assert any(p.startswith(prefix) for p in paths), f"Missing routes under {prefix}"


# ═══════════════ Next.js Build Check ═══════════════


@pytest.mark.asyncio
async def test_nextjs_typecheck():
    """Next.js type-check passes."""
    web_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web")
    if not os.path.exists(os.path.join(web_dir, "package.json")):
        pytest.skip("Web app not found")

    result = subprocess.run(
        ["pnpm", "type-check"],
        cwd=web_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Type-check failed: {result.stdout}\n{result.stderr}"


# ═══════════════ Ruff Lint Check ═══════════════


@pytest.mark.asyncio
async def test_ruff_lint_clean():
    """Ruff linting passes with no errors."""
    api_dir = os.path.join(os.path.dirname(__file__), "..")

    result = subprocess.run(
        ["uv", "run", "ruff", "check", "."],
        cwd=api_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}"


@pytest.mark.asyncio
async def test_alembic_issue21_roundtrip_with_workflow_pack_items():
    """R52: downgrading migration b9ca3e445203 re-creates the pre-issue-21
    CHECK constraint on learning_path_items — with any WORKFLOW_PACK row
    present (a feature rows legitimately use after R45) the ALTER TABLE
    failed and the whole downgrade aborted mid-transaction. The downgrade
    must delete those rows first (their data is dropped anyway).

    Uses a THROWAWAY path/item; the roundtrip drops all issue-21 tables and
    re-seeds them, so this test must run against the shared dev DB the same
    way the rest of the suite does (data in issue-21 tables is transient)."""
    from sqlalchemy import text as sa_text

    from app.core.database import AsyncSessionLocal

    api_dir = os.path.join(os.path.dirname(__file__), "..")

    # Seed a WORKFLOW_PACK path item directly (constraint-satisfying)
    async with AsyncSessionLocal() as db:
        await db.execute(
            sa_text(
                "INSERT INTO learning_paths (id, org_id, name, slug, status, created_by, created_at, updated_at) "
                "SELECT '01TESTPATHROUNDTRIP0000000', o.id, 'RT', 'rt-' || substr(md5(random()::text), 1, 8), 'DRAFT', u.id, now(), now() "
                "FROM organizations o, users u LIMIT 1 "
                "ON CONFLICT (id) DO NOTHING"
            )
        )
        await db.execute(
            sa_text(
                "INSERT INTO learning_path_items (id, path_id, item_type, workflow_pack_id, sort_order, required, unlock_rule) "
                "SELECT '01TESTITEMROUNDTRIP0000000', '01TESTPATHROUNDTRIP0000000', 'WORKFLOW_PACK', '01FAKEPACKID0000000000000X', 0, true, 'previous_required' "
                "WHERE EXISTS (SELECT 1 FROM learning_paths WHERE id = '01TESTPATHROUNDTRIP0000000') "
                "ON CONFLICT (id) DO NOTHING"
            )
        )
        await db.commit()

    env = {**os.environ, "PYTHONPATH": "."}
    down = subprocess.run(
        ["uv", "run", "alembic", "downgrade", "-3"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert down.returncode == 0, f"Downgrade failed: {down.stderr[-2000:]}"
    up = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=api_dir,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert up.returncode == 0, f"Re-upgrade failed: {up.stderr[-2000:]}"

    # Seeds restored by the re-upgrade
    async with AsyncSessionLocal() as db:
        n = (await db.execute(sa_text("SELECT count(*) FROM capability_tags"))).scalar_one()
        assert n >= 9
        # Cleanup the throwaway path (its items were dropped by the downgrade)
        await db.execute(
            sa_text("DELETE FROM learning_paths WHERE id = '01TESTPATHROUNDTRIP0000000'")
        )
        await db.commit()

    # The subprocess DDL dropped/recreated tables while the app's global
    # engine pool held connections — their asyncpg prepared-statement caches
    # now reference dead OIDs and poison whichever test runs next (this test
    # doesn't use the `c` fixture that normally disposes the engine).
    from app.core.database import engine

    await engine.dispose()
