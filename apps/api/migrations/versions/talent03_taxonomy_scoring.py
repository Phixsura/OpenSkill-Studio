"""Add external taxonomy columns to capabilities + capability_score_snapshots table (ADR-015 D1/D3).

Phase 1A: external_ids (JSONB), aliases (JSONB), translations (JSONB) on capabilities.
Phase 1B: capability_score_snapshots table for multi-dimensional scoring audit trail.

Revision ID: talent03a00003
Revises: talent02a00002
Create Date: 2026-09-13 20:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "talent03a00003"
down_revision = "talent02a00002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Phase 1A: External taxonomy interoperability columns on capabilities
    op.add_column(
        "capabilities",
        sa.Column(
            "external_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
    )
    op.add_column(
        "capabilities",
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
    )
    op.add_column(
        "capabilities",
        sa.Column(
            "translations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    # GIN index on external_ids for JSONB containment/path queries
    op.create_index(
        "ix_capabilities_external_ids",
        "capabilities",
        ["external_ids"],
        postgresql_using="gin",
    )

    # Phase 1B: Score snapshot table for multi-dimensional scoring audit trail
    op.create_table(
        "capability_score_snapshots",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "capability_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Numeric(5, 4), nullable=False),
        sa.Column("depth", sa.Numeric(5, 4), nullable=False),
        sa.Column("breadth", sa.Numeric(5, 4), nullable=False),
        sa.Column("recency", sa.Numeric(5, 4), nullable=False),
        sa.Column("velocity", sa.Numeric(5, 4), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("level", sa.Integer, nullable=False),
        sa.Column("evidence_count", sa.Integer, nullable=False),
        sa.Column(
            "verification_mix",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("scoring_version", sa.String(20), nullable=False),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_score_snap_user",
        "capability_score_snapshots",
        ["user_id"],
    )
    op.create_index(
        "ix_score_snap_user_cap",
        "capability_score_snapshots",
        ["user_id", "capability_id"],
    )
    op.create_index(
        "ix_score_snap_computed",
        "capability_score_snapshots",
        ["computed_at"],
    )


def downgrade() -> None:
    op.drop_table("capability_score_snapshots")
    op.drop_index("ix_capabilities_external_ids", table_name="capabilities")
    op.drop_column("capabilities", "translations")
    op.drop_column("capabilities", "aliases")
    op.drop_column("capabilities", "external_ids")
