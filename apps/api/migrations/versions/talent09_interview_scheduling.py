"""talent09: Interview scheduling — slots, stage fields.

Revision ID: talent09a00009
Revises: talent08a00008
"""

import sqlalchemy as sa
from alembic import op

revision = "talent09a00009"
down_revision = "talent08a00008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Interview slots table --
    op.create_table(
        "talent_interview_slots",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "interview_stage_id",
            sa.String(26),
            sa.ForeignKey("interview_stages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "proposed_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="proposed",
        ),
        sa.Column("meeting_url", sa.String(500), nullable=True),
        sa.Column("meeting_notes", sa.Text(), nullable=True),
        sa.Column(
            "accepted_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
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
        "ix_interview_slots_stage",
        "talent_interview_slots",
        ["interview_stage_id", "status"],
    )
    op.create_index(
        "ix_interview_slots_proposed_by",
        "talent_interview_slots",
        ["proposed_by"],
    )

    # -- Add columns to interview_stages --
    op.add_column(
        "interview_stages",
        sa.Column("scheduled_timezone", sa.String(50), nullable=True),
    )
    op.add_column(
        "interview_stages",
        sa.Column("meeting_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "interview_stages",
        sa.Column("duration_minutes", sa.SmallInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("interview_stages", "duration_minutes")
    op.drop_column("interview_stages", "meeting_url")
    op.drop_column("interview_stages", "scheduled_timezone")
    op.drop_index("ix_interview_slots_proposed_by", "talent_interview_slots")
    op.drop_index("ix_interview_slots_stage", "talent_interview_slots")
    op.drop_table("talent_interview_slots")
