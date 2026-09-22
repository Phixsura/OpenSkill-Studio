"""eco06 raw payload snapshots for replay (ADR-016 §42).

Revision ID: eco06a00006
Revises: eco05a00005
Create Date: 2026-09-22
"""

import sqlalchemy as sa
from alembic import op

revision: str = "eco06a00006"
down_revision: str = "eco05a00005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eco_raw_snapshots",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "source_id",
            sa.String(26),
            sa.ForeignKey("eco_sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("content_length", sa.Integer(), nullable=False),
        sa.Column("parser_version", sa.String(20), nullable=False),
        sa.Column(
            "fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("source_id", "raw_hash", name="uq_eco_raw_snapshot"),
    )
    op.create_index("ix_eco_raw_snapshots_source", "eco_raw_snapshots", ["source_id", "fetched_at"])


def downgrade() -> None:
    op.drop_index("ix_eco_raw_snapshots_source", table_name="eco_raw_snapshots")
    op.drop_table("eco_raw_snapshots")
