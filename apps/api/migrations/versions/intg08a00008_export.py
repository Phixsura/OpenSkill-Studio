"""Governed warehouse export streams + runs (ADR-018 §16.2, P9)

Revision ID: intg08a00008
Revises: intg07a00007
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg08a00008"
down_revision = "intg07a00007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_export_streams",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("dataset", sa.String(50), nullable=False),
        sa.Column("field_allowlist", JSONB, nullable=False, server_default="[]"),
        sa.Column("anonymize", JSONB, nullable=False, server_default="{}"),
        sa.Column("schedule", sa.String(20), nullable=False),
        sa.Column("cursor", JSONB, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_export_org_name", "intg_export_streams", ["org_id", "name"], unique=True
    )
    op.create_table(
        "intg_export_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "stream_id",
            sa.String(26),
            sa.ForeignKey("intg_export_streams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("cursor_from", JSONB, nullable=False, server_default="{}"),
        sa.Column("cursor_to", JSONB, nullable=False, server_default="{}"),
        sa.Column("row_count", sa.Integer, nullable=False),
        sa.Column("parts", JSONB, nullable=False, server_default="[]"),
        sa.Column("manifest_key", sa.String(500), nullable=True),
        sa.Column("error", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_intg_export_runs", "intg_export_runs", ["stream_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_intg_export_runs", table_name="intg_export_runs")
    op.drop_table("intg_export_runs")
    op.drop_index("uq_intg_export_org_name", table_name="intg_export_streams")
    op.drop_table("intg_export_streams")
