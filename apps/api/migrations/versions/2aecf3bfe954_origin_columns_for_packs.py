"""Add origin tracking columns to skills, exercises, categories, templates.

Revision ID: 2aecf3bfe954
Revises: 102e6638eaa1
Create Date: 2026-08-19
"""

import sqlalchemy as sa
from alembic import op

revision: str = "2aecf3bfe954"
down_revision: str | None = "102e6638eaa1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("skills", "exercises", "skill_categories", "project_templates"):
        op.add_column(table, sa.Column("origin_pack_id", sa.String(26), nullable=True))
        op.add_column(table, sa.Column("origin_release_id", sa.String(26), nullable=True))
        op.add_column(table, sa.Column("origin_component_id", sa.String(100), nullable=True))
        op.add_column(table, sa.Column("locally_modified", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    for table in ("skills", "exercises", "skill_categories", "project_templates"):
        op.drop_column(table, "locally_modified")
        op.drop_column(table, "origin_component_id")
        op.drop_column(table, "origin_release_id")
        op.drop_column(table, "origin_pack_id")
