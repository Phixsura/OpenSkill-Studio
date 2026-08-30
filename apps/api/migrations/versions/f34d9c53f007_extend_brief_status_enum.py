"""extend_brief_status_enum

Revision ID: f34d9c53f007
Revises: af18bccf7908
Create Date: 2026-08-18 16:30:39.700595

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f34d9c53f007"
down_revision: str | None = "af18bccf7908"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add new brief_status enum values for full commercial lifecycle
    for value in ("OPEN", "ASSIGNED", "IN_PRODUCTION", "REVIEW", "CANCELLED"):
        op.execute(f"ALTER TYPE brief_status ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Enum values cannot be removed in PostgreSQL — no-op
    pass
