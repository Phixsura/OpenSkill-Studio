"""Add MARKDOWN to item_type enum

Revision ID: e8b13fa92c4d
Revises: d5a927f18b3c
Create Date: 2026-08-15
"""

from alembic import op

revision = "e8b13fa92c4d"
down_revision = "d5a927f18b3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PG cannot ADD VALUE to an enum inside a transaction block
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE item_type ADD VALUE IF NOT EXISTS 'MARKDOWN'")


def downgrade() -> None:
    # PG enums cannot drop values; leaving the extra value is harmless
    pass
