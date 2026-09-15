"""talent05 — scorecard templates + interview scorecards.

Revision ID: talent05a00005
Revises: talent04a00004
Create Date: 2026-09-14
"""

import sqlalchemy as sa
from alembic import op

revision = "talent05a00005"
down_revision = "talent04a00004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_scorecard_templates",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("criteria", sa.JSON, server_default="[]", nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            server_default="active",
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
    op.create_index(
        "ix_scorecard_tmpl_org",
        "talent_scorecard_templates",
        ["org_id"],
    )

    op.create_table(
        "talent_interview_scorecards",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "interview_stage_id",
            sa.String(26),
            sa.ForeignKey("interview_stages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "template_id",
            sa.String(26),
            sa.ForeignKey("talent_scorecard_templates.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "interviewer_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ratings", sa.JSON, server_default="{}", nullable=False),
        sa.Column("overall_rating", sa.SmallInteger, nullable=True),
        sa.Column("recommendation", sa.String(30), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index(
        "ix_scorecard_interview",
        "talent_interview_scorecards",
        ["interview_stage_id"],
    )
    op.create_index(
        "ix_scorecard_interviewer",
        "talent_interview_scorecards",
        ["interviewer_id"],
    )


def downgrade() -> None:
    op.drop_table("talent_interview_scorecards")
    op.drop_table("talent_scorecard_templates")
