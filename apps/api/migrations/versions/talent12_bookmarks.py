"""talent12: opportunity bookmarks

Revision ID: talent12a00012
Revises: talent11a00011
"""

from alembic import op
import sqlalchemy as sa

revision = "talent12a00012"
down_revision = "talent11a00011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_opportunity_bookmarks",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "opportunity_id",
            sa.String(26),
            sa.ForeignKey("talent_opportunities.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "user_id", "opportunity_id", name="uq_user_opportunity_bookmark"
        ),
    )


def downgrade() -> None:
    op.drop_table("talent_opportunity_bookmarks")
