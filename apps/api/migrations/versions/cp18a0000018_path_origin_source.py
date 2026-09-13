"""learning_paths.origin_source_path_id — listing-less install dedupe key.

R129[M2]: manual-grant learning-path installs have no origin_listing_id;
deduping them by name collides with the org's own same-named local paths.
Record the source path id on each installed copy as a reliable idempotency
key (partial unique on (org, source) among live listing-less copies).

Revision ID: cp18a0000018
Revises: cp17f0000017
"""

import sqlalchemy as sa
from alembic import op

revision = "cp18a0000018"
down_revision = "cp17f0000017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "learning_paths",
        sa.Column("origin_source_path_id", sa.String(length=26), nullable=True),
    )
    op.create_index(
        "uq_paths_org_source_live",
        "learning_paths",
        ["org_id", "origin_source_path_id"],
        unique=True,
        postgresql_where=sa.text(
            "origin_source_path_id IS NOT NULL "
            "AND origin_listing_id IS NULL "
            "AND status != 'ARCHIVED'"
        ),
    )


def downgrade() -> None:
    op.drop_index("uq_paths_org_source_live", table_name="learning_paths")
    op.drop_column("learning_paths", "origin_source_path_id")
