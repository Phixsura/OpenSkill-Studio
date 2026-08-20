"""widen_version_columns

Revision ID: d4e5f6071829
Revises: c3d4e5f60718
Create Date: 2026-08-20 10:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6071829"
down_revision: str | None = "c3d4e5f60718"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Widen version columns from VARCHAR(20) to VARCHAR(50)
    # to support pre-release semver versions like 1.0.0-alpha.1
    op.alter_column(
        "skill_pack_releases",
        "version",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=False,
    )
    op.alter_column(
        "skill_pack_installations",
        "installed_version",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "skill_pack_installations",
        "installed_version",
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=False,
    )
    op.alter_column(
        "skill_pack_releases",
        "version",
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=False,
    )
