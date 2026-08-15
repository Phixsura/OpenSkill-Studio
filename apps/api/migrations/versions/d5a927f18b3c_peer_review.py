"""peer review rounds + assessments (Moodle Workshop model, simplified)

Revision ID: d5a927f18b3c
Revises: c93d15e07f2a
Create Date: 2026-08-15
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d5a927f18b3c"
down_revision = "c93d15e07f2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    phase = postgresql.ENUM(
        "SETUP", "ASSESSMENT", "CLOSED", name="peer_review_phase", create_type=False
    )
    phase.create(op.get_bind(), checkfirst=True)
    status = postgresql.ENUM(
        "PENDING", "SUBMITTED", name="peer_assessment_status", create_type=False
    )
    status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "peer_review_rounds",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("project_id", sa.String(26), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("num_reviews", sa.Integer(), nullable=False),
        sa.Column("anonymous", sa.Boolean(), nullable=False),
        sa.Column("include_self_review", sa.Boolean(), nullable=False),
        sa.Column("phase", phase, nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pr_rounds_project", "peer_review_rounds", ["project_id"])

    op.create_table(
        "peer_assessments",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("round_id", sa.String(26), nullable=False),
        sa.Column("submission_id", sa.String(26), nullable=False),
        sa.Column("reviewer_id", sa.String(26), nullable=False),
        sa.Column("is_self_review", sa.Boolean(), nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("score_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["round_id"], ["peer_review_rounds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_peer_assessment",
        "peer_assessments",
        ["round_id", "submission_id", "reviewer_id"],
        unique=True,
    )
    op.create_index("ix_peer_assessments_reviewer", "peer_assessments", ["round_id", "reviewer_id"])


def downgrade() -> None:
    op.drop_index("ix_peer_assessments_reviewer", table_name="peer_assessments")
    op.drop_index("uq_peer_assessment", table_name="peer_assessments")
    op.drop_table("peer_assessments")
    op.drop_index("ix_pr_rounds_project", table_name="peer_review_rounds")
    op.drop_table("peer_review_rounds")
    postgresql.ENUM(name="peer_assessment_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="peer_review_phase").drop(op.get_bind(), checkfirst=True)
