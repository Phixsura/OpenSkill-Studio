"""anonymous-to-login identity links (ADR-017 §4.17, round 210)

Revision ID: exp15a00015
Revises: exp14a00014
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "exp15a00015"
down_revision = "exp14a00014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "experiment_identity_links",
        sa.Column("anonymous_id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_experiment_identity_links_user",
        "experiment_identity_links",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_experiment_identity_links_user",
                  table_name="experiment_identity_links")
    op.drop_table("experiment_identity_links")
