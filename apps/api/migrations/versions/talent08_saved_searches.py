"""talent08: saved searches for talent rediscovery

Revision ID: talent08a00008
Revises: talent07a00007
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "talent08a00008"
down_revision = "talent07a00007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_saved_searches",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("search_type", sa.String(20), nullable=False),
        sa.Column("search_criteria", JSONB, nullable=False, server_default="{}"),
        sa.Column("notify_frequency", sa.String(20), nullable=False, server_default="never"),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_talent_saved_searches_org_id", "talent_saved_searches", ["org_id"])
    op.create_index("ix_talent_saved_searches_created_by", "talent_saved_searches", ["created_by"])
    op.create_index(
        "ix_talent_saved_searches_search_type", "talent_saved_searches", ["search_type"]
    )


# NOTE: downgrade drops tables — run in order
def downgrade() -> None:
    op.drop_index("ix_talent_saved_searches_search_type")
    op.drop_index("ix_talent_saved_searches_created_by")
    op.drop_index("ix_talent_saved_searches_org_id")
    op.drop_table("talent_saved_searches")
