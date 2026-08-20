"""add helpful_count, reply columns and review_helpful_votes table

Revision ID: c4d5e6f70a10
Revises: b3c4d5e6f709
Create Date: 2026-08-20 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d5e6f70a10"
down_revision: str | None = "b3c4d5e6f709"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add missing columns to pack_reviews
    op.add_column(
        "pack_reviews",
        sa.Column("helpful_count", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "pack_reviews",
        sa.Column("reply_text", sa.String(1000), nullable=True),
    )
    op.add_column(
        "pack_reviews",
        sa.Column("reply_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create review_helpful_votes table
    op.create_table(
        "review_helpful_votes",
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "review_id",
            sa.String(26),
            sa.ForeignKey("pack_reviews.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("review_helpful_votes")
    op.drop_column("pack_reviews", "reply_at")
    op.drop_column("pack_reviews", "reply_text")
    op.drop_column("pack_reviews", "helpful_count")
