"""exp05 decision records & promotion drafts (ADR-017 §4.9-§4.10)

Revision ID: exp05a00005
Revises: exp04a00004
Create Date: 2026-09-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "exp05a00005"
down_revision: str | None = "exp04a00004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiment_decision_records",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("experiment_id", sa.String(length=26), nullable=False),
        sa.Column("experiment_version", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=14), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(length=20), nullable=False),
        sa.Column("analysis_type", sa.String(length=14), nullable=False),
        sa.Column("analysis_result_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "uncertainty", postgresql.JSONB(astext_type=sa.Text()), server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "segments", postgresql.JSONB(astext_type=sa.Text()), server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "guardrail_outcome", postgresql.JSONB(astext_type=sa.Text()), server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "evidence", postgresql.JSONB(astext_type=sa.Text()), server_default="{}",
            nullable=False,
        ),
        sa.Column("approver_user_id", sa.String(length=26), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approver_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_experiment_decision_terminal",
        "experiment_decision_records",
        ["experiment_id"],
        unique=True,
        postgresql_where=sa.text("decision IN ('promote', 'reject')"),
    )
    op.create_index(
        "ix_experiment_decision_domain", "experiment_decision_records", ["domain", "decision"]
    )

    op.create_table(
        "experiment_promotion_drafts",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("decision_record_id", sa.String(length=26), nullable=False),
        sa.Column("target_type", sa.String(length=30), nullable=False),
        sa.Column("target_ref", sa.String(length=64), nullable=False),
        sa.Column(
            "draft_payload", postgresql.JSONB(astext_type=sa.Text()), server_default="{}",
            nullable=False,
        ),
        sa.Column("status", sa.String(length=10), server_default="draft", nullable=False),
        sa.Column("approved_by", sa.String(length=26), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_ref", sa.String(length=64), nullable=True),
        sa.Column("apply_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["experiment_decision_records.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_experiment_promotion_drafts_status", "experiment_promotion_drafts", ["status"]
    )


def downgrade() -> None:
    op.drop_table("experiment_promotion_drafts")
    op.drop_table("experiment_decision_records")
