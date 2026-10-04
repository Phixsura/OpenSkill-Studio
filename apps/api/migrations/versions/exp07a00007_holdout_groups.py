"""exp07 global holdout groups (ADR-017 §4.12 v2)

Revision ID: exp07a00007
Revises: exp06a00006
Create Date: 2026-10-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "exp07a00007"
down_revision: str | None = "exp06a00006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiment_holdout_groups",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("domain", sa.String(length=20), nullable=False),
        sa.Column("scope_org_id", sa.String(length=26), nullable=True),
        sa.Column("holdout_bp", sa.Integer(), nullable=False),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=10), server_default="active", nullable=False),
        sa.Column("created_by", sa.String(length=26), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["scope_org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(
        "ix_experiment_holdout_groups_domain",
        "experiment_holdout_groups",
        ["domain", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_experiment_holdout_groups_domain", table_name="experiment_holdout_groups")
    op.drop_table("experiment_holdout_groups")
