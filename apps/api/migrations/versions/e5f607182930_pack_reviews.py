"""pack_reviews

Revision ID: e5f607182930
Revises: d4e5f6071829
Create Date: 2026-08-20 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5f607182930"
down_revision: str | None = "d4e5f6071829"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create pack_reviews table
    op.create_table(
        "pack_reviews",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("skill_packs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )
    op.create_index(
        "uq_review_pack_user", "pack_reviews", ["pack_id", "user_id"], unique=True
    )
    op.create_index(
        "ix_reviews_pack_created", "pack_reviews", ["pack_id", "created_at"]
    )

    # Add review_count and average_rating to skill_packs
    op.add_column(
        "skill_packs",
        sa.Column("review_count", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "skill_packs",
        sa.Column("average_rating", sa.Float, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("skill_packs", "average_rating")
    op.drop_column("skill_packs", "review_count")
    op.drop_index("ix_reviews_pack_created", table_name="pack_reviews")
    op.drop_index("uq_review_pack_user", table_name="pack_reviews")
    op.drop_table("pack_reviews")
