"""eco10: (detected_at, id) index on the change ledger (ADR-016 §99)

The Atom firehose and the dashboard change-feed order the WHOLE table by
detected_at DESC LIMIT n with no filter, and the delta export sorts by
(detected_at, id) — every existing index leads with a filter column, so at
scale both paths degrade to a full-table sort. Composite (detected_at, id)
serves the backward scan for newest-first AND the delta cursor's
lexicographic order directly.

Revision ID: eco10a00010
Revises: eco09a00009
Create Date: 2026-09-27
"""

from alembic import op

revision: str = "eco10a00010"
down_revision: str = "eco09a00009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # CONCURRENTLY: hot append-only table (same posture as eco08)
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_eco_changes_detected_id",
            "eco_change_events",
            ["detected_at", "id"],
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    op.drop_index("ix_eco_changes_detected_id", table_name="eco_change_events")
