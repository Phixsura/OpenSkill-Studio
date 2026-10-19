"""R490: migration DOWNGRADE round-trip — a never-driven-code probe.

Every migration ships a downgrade() that production never runs (the same
gap class as R11's never-driven scheduled syncs and R16's exports). A
broken downgrade is discovered exactly when an operator needs an emergency
rollback. This probe runs the full chain base→head→base→head against a
THROWAWAY database (never the shared dev DB — a mid-battery drop of live
fabric tables would poison concurrent suites) and asserts:

- head→base leaves nothing but alembic_version (no orphan tables/types);
- base→head after the round trip reproduces the same table set;
- both directions exit 0 (every downgrade body actually executes).
"""

import os
import subprocess
import uuid

import pytest

pytestmark = pytest.mark.timeout(600)

API_DIR = os.path.join(os.path.dirname(__file__), "..")


def _admin_dsn_and_scratch() -> tuple[str, str, str]:
    from app.config import settings

    url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    base, _, _dbname = url.rpartition("/")
    scratch = f"intg_roundtrip_{uuid.uuid4().hex[:10]}"
    return f"{base}/postgres", f"{base}/{scratch}", scratch


async def _tables(dsn: str) -> set[str]:
    import asyncpg

    conn = await asyncpg.connect(dsn)
    try:
        rows = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        return {r["tablename"] for r in rows}
    finally:
        await conn.close()


def _alembic(args: list[str], scratch_url: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["DATABASE_URL"] = scratch_url.replace("postgresql://", "postgresql+asyncpg://")
    return subprocess.run(
        ["uv", "run", "alembic", *args],
        cwd=API_DIR,
        capture_output=True,
        text=True,
        timeout=420,
        env=env,
    )


@pytest.mark.asyncio
async def test_full_downgrade_upgrade_round_trip_on_scratch_db():
    import asyncpg

    admin_dsn, scratch_dsn, scratch = _admin_dsn_and_scratch()
    admin = await asyncpg.connect(admin_dsn)
    await admin.execute(f'CREATE DATABASE "{scratch}"')
    await admin.close()
    try:
        up1 = _alembic(["upgrade", "head"], scratch_dsn)
        assert up1.returncode == 0, f"initial upgrade failed: {up1.stderr[-2000:]}"
        tables_head = await _tables(scratch_dsn)
        assert "intg_export_streams" in tables_head and len(tables_head) > 50

        down = _alembic(["downgrade", "base"], scratch_dsn)
        assert down.returncode == 0, f"downgrade to base failed: {down.stderr[-2000:]}"
        tables_base = await _tables(scratch_dsn)
        # alembic_version may remain; every model table must be gone.
        assert tables_base <= {"alembic_version"}, f"orphans: {sorted(tables_base)[:10]}"

        up2 = _alembic(["upgrade", "head"], scratch_dsn)
        assert up2.returncode == 0, f"re-upgrade failed: {up2.stderr[-2000:]}"
        tables_head2 = await _tables(scratch_dsn)
        assert tables_head2 == tables_head
    finally:
        admin = await asyncpg.connect(admin_dsn)
        try:
            await admin.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = $1 AND pid <> pg_backend_pid()",
                scratch,
            )
            await admin.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
        finally:
            await admin.close()
