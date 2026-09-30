"""eco09: per-user feed-token generation (revocation by rotation, ADR-016 §94.6)

Revision ID: eco09a00009
Revises: eco08a00008
Create Date: 2026-09-26
"""

import sqlalchemy as sa
from alembic import op

revision: str = "eco09a00009"
down_revision: str = "eco08a00008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eco_feed_token_state",
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("generation", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "rotated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("eco_feed_token_state")
