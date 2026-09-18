"""Extend OrgRole enum with employer roles + add org_type column (ADR-015 §16)

Revision ID: talent02a00002
Revises: talent01a00001
Create Date: 2026-09-13 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "talent02a00002"
down_revision: str | None = "talent01a00001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Extend OrgRole enum with employer roles.
    # ADD VALUE is non-reversible in Postgres — values cannot be removed.
    # IF NOT EXISTS prevents errors on re-run.
    op.execute("ALTER TYPE org_role ADD VALUE IF NOT EXISTS 'hiring_manager'")
    op.execute("ALTER TYPE org_role ADD VALUE IF NOT EXISTS 'recruiter'")
    op.execute("ALTER TYPE org_role ADD VALUE IF NOT EXISTS 'interviewer'")

    # Add org_type column to distinguish training orgs from employer orgs.
    # Default 'school' so all existing orgs retain their current semantics.
    op.add_column(
        "organizations",
        sa.Column("org_type", sa.String(20), server_default="school", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("organizations", "org_type")
    # Note: Postgres enum values added via ALTER TYPE ... ADD VALUE cannot
    # be removed. The three employer roles will remain in the enum even
    # after downgrade, but they are inert (no rows reference them).
