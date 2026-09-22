"""eco05 security advisories registry (ADR-016 §38).

Revision ID: eco05a00005
Revises: eco04a00004
Create Date: 2026-09-22
"""

import sqlalchemy as sa
from alembic import op

revision: str = "eco05a00005"
down_revision: str = "eco04a00004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eco_security_advisories",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("advisory_ref", sa.String(100), nullable=False, unique=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("affected_kind", sa.String(30), nullable=True),
        sa.Column("affected_ref", sa.String(300), nullable=False),
        sa.Column("affected_range", sa.String(100), nullable=True),
        sa.Column("fixed_in", sa.String(50), nullable=True),
        sa.Column(
            "source_observation_id",
            sa.String(26),
            sa.ForeignKey("eco_observations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_eco_advisories_status", "eco_security_advisories", ["status", "severity"]
    )


def downgrade() -> None:
    op.drop_index("ix_eco_advisories_status", table_name="eco_security_advisories")
    op.drop_table("eco_security_advisories")
