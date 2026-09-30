"""eco07 DB-level watch-item dedupe (ADR-016 §3.12 / R127).

The §3.12 uniqueness probe was service-level only: two concurrent add_item
calls for the same target both passed the SELECT and double-inserted —
doubling every notification for that target. Partial unique indexes give the
race a database-level backstop (NULLs make a single composite constraint
useless here, hence one index per target column).

Revision ID: eco07a00007
Revises: eco06a00006
Create Date: 2026-09-24
"""

from alembic import op

revision: str = "eco07a00007"
down_revision: str = "eco06a00006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # De-duplicate first (keep the oldest row per target) or index creation fails
    op.execute(
        """
        DELETE FROM eco_watch_items a USING eco_watch_items b
        WHERE a.watchlist_id = b.watchlist_id
          AND a.target_kind = b.target_kind
          AND a.target_id IS NOT DISTINCT FROM b.target_id
          AND a.target_ref IS NOT DISTINCT FROM b.target_ref
          AND a.id > b.id
        """
    )
    op.create_index(
        "uq_eco_watch_item_target",
        "eco_watch_items",
        ["watchlist_id", "target_kind", "target_id"],
        unique=True,
        postgresql_where="target_id IS NOT NULL",
    )
    op.create_index(
        "uq_eco_watch_item_ref",
        "eco_watch_items",
        ["watchlist_id", "target_kind", "target_ref"],
        unique=True,
        postgresql_where="target_ref IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_index("uq_eco_watch_item_ref", table_name="eco_watch_items")
    op.drop_index("uq_eco_watch_item_target", table_name="eco_watch_items")
