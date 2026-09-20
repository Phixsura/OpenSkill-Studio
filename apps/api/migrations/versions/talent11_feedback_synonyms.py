"""talent11: application feedback table.

Revision ID: talent11a00011
Revises: talent10a00010
"""

import sqlalchemy as sa
from alembic import op

revision = "talent11a00011"
down_revision = "talent10a00010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_application_feedback",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "application_id",
            sa.String(26),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("feedback_type", sa.String(30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "visibility",
            sa.String(30),
            nullable=False,
            server_default="employer_only",
        ),
        sa.Column(
            "author_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_app_feedback_app",
        "talent_application_feedback",
        ["application_id"],
    )
    op.create_index(
        "ix_app_feedback_author",
        "talent_application_feedback",
        ["author_id"],
    )
    op.create_index(
        "ix_app_feedback_type",
        "talent_application_feedback",
        ["feedback_type"],
    )


# NOTE: downgrade drops tables — run in order
def downgrade() -> None:
    op.drop_index("ix_app_feedback_type", table_name="talent_application_feedback")
    op.drop_index("ix_app_feedback_author", table_name="talent_application_feedback")
    op.drop_index("ix_app_feedback_app", table_name="talent_application_feedback")
    op.drop_table("talent_application_feedback")
