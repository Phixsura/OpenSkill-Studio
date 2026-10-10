"""Bulk import jobs + row errors (ADR-018 §16.1, P8)

Revision ID: intg07a00007
Revises: intg06a00006
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg07a00007"
down_revision = "intg06a00006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_import_jobs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("template_version", sa.Integer, nullable=False),
        sa.Column("mode", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("dry_stats", JSONB, nullable=False, server_default="{}"),
        sa.Column("stats", JSONB, nullable=False, server_default="{}"),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_import_org", "intg_import_jobs", ["org_id", "created_at"])
    op.create_index(
        "uq_intg_import_idem",
        "intg_import_jobs",
        ["org_id", "idempotency_key"],
        unique=True,
    )
    op.create_table(
        "intg_import_row_errors",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "job_id",
            sa.String(26),
            sa.ForeignKey("intg_import_jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("row_number", sa.Integer, nullable=False),
        sa.Column("column", sa.String(100), nullable=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("message", sa.String(300), nullable=False),
        sa.Column("raw_row", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_intg_import_errors", "intg_import_row_errors", ["job_id", "row_number"]
    )


def downgrade() -> None:
    op.drop_index("ix_intg_import_errors", table_name="intg_import_row_errors")
    op.drop_table("intg_import_row_errors")
    op.drop_index("uq_intg_import_idem", table_name="intg_import_jobs")
    op.drop_index("ix_intg_import_org", table_name="intg_import_jobs")
    op.drop_table("intg_import_jobs")
