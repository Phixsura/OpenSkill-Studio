"""Fix creator_assignments.assigned_by: ondelete='SET NULL' requires nullable

Revision ID: c1db4f556304
Revises: b9ca3e445203
Create Date: 2026-08-23 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1db4f556304"
down_revision: str | None = "b9ca3e445203"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # assigned_by has ondelete='SET NULL' but was created NOT NULL —
    # deleting the assigning user would violate the constraint.
    op.alter_column(
        "creator_assignments",
        "assigned_by",
        existing_type=sa.String(26),
        nullable=True,
    )


def downgrade() -> None:
    # Revert to NOT NULL (will fail if any NULLs exist)
    op.alter_column(
        "creator_assignments",
        "assigned_by",
        existing_type=sa.String(26),
        nullable=False,
    )
