"""R573: repo-wide SEVERE schema drift guard.

The fabric drift guard (test_integrations_wiring_db) is intg_*-scoped
because older epics carry ~230 benign diffs (nullable flags, FK ondelete
restatements, index naming). That scoping is how skill_passports.alumni_mode
shipped as a model column with NO migration — every ORM SELECT of the model
500'd on a migrated database and 3,368 unit tests stayed green (R572).

This guard runs over the WHOLE schema but only fails on the drift classes
that break production outright:

  - add_table / remove_table    (model without a migration, or vice versa)
  - add_column / remove_column  (UndefinedColumnError on ORM selects)
  - modify_type                 (JSON vs JSONB & friends)

Benign legacy classes (modify_nullable, FK restatements, index diffs) are
deliberately ignored here — tightening those is a separate cleanup.
"""

import pathlib

import pytest

SEVERE = {"add_table", "remove_table", "add_column", "remove_column", "modify_type"}


@pytest.mark.asyncio
async def test_no_severe_model_migration_drift_repo_wide():
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    import app.controlplane.models  # noqa: F401
    import app.ecosystem.models  # noqa: F401
    import app.experiments.models  # noqa: F401
    import app.integrations.models  # noqa: F401
    import app.talent.models  # noqa: F401
    from app.core.database import engine
    from app.models import Base  # same aggregator migrations/env.py uses

    def _diffs(sync_conn):
        ctx = MigrationContext.configure(sync_conn, opts={"compare_type": True})
        return compare_metadata(ctx, Base.metadata)

    async with engine.connect() as conn:
        diffs = await conn.run_sync(_diffs)
    await engine.dispose()

    severe = []
    for d in diffs:
        op = d[0][0] if isinstance(d, list) else d[0]
        if op in SEVERE:
            severe.append(d)
    assert not severe, (
        f"{len(severe)} severe model/migration drift(s) — a model changed "
        f"without a migration (or the reverse): {severe[:5]}"
    )


def test_single_migration_head():
    """R618: two sessions adding migrations concurrently (this repo runs
    parallel worktrees) can each branch off the same parent — `alembic
    upgrade head` then FAILS at deploy time with 'multiple heads'. Catch the
    branch at test time, where the fix (a merge revision or re-parenting) is
    cheap."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"))
    cfg.set_main_option(
        "script_location",
        str(pathlib.Path(__file__).resolve().parent.parent / "migrations"),
    )
    heads = ScriptDirectory.from_config(cfg).get_heads()
    assert len(heads) == 1, f"branched migration history — multiple heads: {heads}"
