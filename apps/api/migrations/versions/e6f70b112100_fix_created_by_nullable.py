"""Fix created_by columns: model declares nullable=True but migrations created nullable=False

Revision ID: e6f70b112100
Revises: d5e6f70b1120
Create Date: 2026-08-22 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e6f70b112100"
down_revision: str | None = "d5e6f70b1120"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Fix nullable mismatch: models declare nullable=True but initial
    # migrations created these columns with nullable=False.
    # When a user is deleted and ondelete='SET NULL' fires, the DB
    # must allow NULLs in these columns.
    tables = [
        "organizations",
        "org_invite_links",
        "projects",
        "skill_categories",
        "skills",
        "exercises",
        "skill_packs",
        "learning_paths",
    ]
    for table in tables:
        op.alter_column(
            table,
            "created_by",
            existing_type=sa.String(26),
            nullable=True,
        )


def downgrade() -> None:
    # Revert to NOT NULL (will fail if any NULLs exist)
    tables = [
        "organizations",
        "org_invite_links",
        "projects",
        "skill_categories",
        "skills",
        "exercises",
        "skill_packs",
        "learning_paths",
    ]
    for table in tables:
        op.alter_column(
            table,
            "created_by",
            existing_type=sa.String(26),
            nullable=False,
        )
