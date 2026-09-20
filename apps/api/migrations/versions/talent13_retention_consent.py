"""talent13: consent log table for data retention/GDPR audit.

Revision ID: talent13a00013
Revises: talent12a00012
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "talent13a00013"
down_revision = "talent12a00012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_consent_log",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("consent_type", sa.String(50), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("details", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_consent_log_user_id", "talent_consent_log", ["user_id"])
    op.create_index("ix_consent_log_consent_type", "talent_consent_log", ["consent_type"])
    op.create_index("ix_consent_log_created_at", "talent_consent_log", ["created_at"])


# NOTE: downgrade drops tables — run in order
def downgrade() -> None:
    op.drop_index("ix_consent_log_created_at")
    op.drop_index("ix_consent_log_consent_type")
    op.drop_index("ix_consent_log_user_id")
    op.drop_table("talent_consent_log")
