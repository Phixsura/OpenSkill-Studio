"""One live installed copy per (org, origin listing) — R123[L6/L14].

The R113[M1] idempotency pre-check is SELECT-only: two concurrent install
POSTs both see no prior copy and both mint one. Partial unique index turns
the race loser into an IntegrityError the service maps to the winner's row.

Revision ID: cp17f0000017
Revises: cp16d0000016
"""

import sqlalchemy as sa
from alembic import op

revision = "cp17f0000017"
down_revision = "cp16d0000016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Pre-existing duplicate copies (the race this index closes) would abort
    # the CREATE — suffix all but the newest per (org, listing) first.
    op.execute(
        sa.text(
            """
            UPDATE learning_paths lp SET origin_listing_id = NULL
            WHERE lp.origin_listing_id IS NOT NULL
              AND lp.status != 'ARCHIVED'
              AND lp.id NOT IN (
                SELECT DISTINCT ON (org_id, origin_listing_id) id
                FROM learning_paths
                WHERE origin_listing_id IS NOT NULL AND status != 'ARCHIVED'
                ORDER BY org_id, origin_listing_id, created_at DESC
              )
            """
        )
    )
    op.create_index(
        "uq_paths_org_origin_live",
        "learning_paths",
        ["org_id", "origin_listing_id"],
        unique=True,
        postgresql_where=sa.text("origin_listing_id IS NOT NULL AND status != 'ARCHIVED'"),
    )


def downgrade() -> None:
    op.drop_index("uq_paths_org_origin_live", table_name="learning_paths")
