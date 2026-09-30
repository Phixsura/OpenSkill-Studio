"""eco08 hot-path indexes (R137).

Two per-change-event queries had no usable index:
- notify fan-out probes eco_watch_items by target_id (only the watchlist_id
  prefix was indexed) — a seq scan on every change event;
- the watch feed reads eco_change_events by canonical_entity_id ordered by
  detected_at (the existing composite leads with entity_kind, so a bare
  canonical_entity_id lookup cannot use it).

Revision ID: eco08a00008
Revises: eco07a00007
Create Date: 2026-09-24
"""

from alembic import op

revision: str = "eco08a00008"
down_revision: str = "eco07a00007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # CONCURRENTLY: eco_change_events is a hot append-only table — a plain
    # CREATE INDEX takes a write lock for the whole build. Requires running
    # outside the migration transaction.
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_eco_watch_items_target",
            "eco_watch_items",
            ["target_id"],
            postgresql_where="target_id IS NOT NULL",
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_eco_changes_canonical",
            "eco_change_events",
            ["canonical_entity_id", "detected_at"],
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    op.drop_index("ix_eco_changes_canonical", table_name="eco_change_events")
    op.drop_index("ix_eco_watch_items_target", table_name="eco_watch_items")
