"""learning_paths.origin_listing_id — paid-content provenance (R113[H0]).

R113[H0]: install_from_listing forks a purchased path into the buyer org as a
plain LearningPath with no origin marker, and create_listing's ownership check
(org_id == seller_org_id) is satisfied by the copy — a buyer could re-list the
purchased copy for sale. Skills/templates carry origin_pack_id for exactly
this gate (R91[H1]/R101[H19]); learning paths were the missing product type.

Revision ID: cp15c0000015
Revises: cp14b0000014
"""

import sqlalchemy as sa
from alembic import op

revision = "cp15c0000015"
down_revision = "cp14b0000014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "learning_paths",
        sa.Column("origin_listing_id", sa.String(length=26), nullable=True),
    )
    op.create_index(
        "ix_paths_origin_listing",
        "learning_paths",
        ["origin_listing_id"],
        postgresql_where=sa.text("origin_listing_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_paths_origin_listing", table_name="learning_paths")
    op.drop_column("learning_paths", "origin_listing_id")
