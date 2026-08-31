"""Learning paths — curriculum composition

Revision ID: 10fbb2faf2d0
Revises: 2aecf3bfe954
Create Date: 2026-08-19
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PGENUM

revision: str = "10fbb2faf2d0"
down_revision: str | None = "2aecf3bfe954"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # learning_paths
    op.create_table(
        "learning_paths",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            PGENUM("DRAFT", "PUBLISHED", "ARCHIVED", name="content_status", create_type=False),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_path_org_slug", "learning_paths", ["org_id", "slug"], unique=True)
    op.create_index("ix_paths_org_status", "learning_paths", ["org_id", "status"])

    # path_item_type enum
    op.execute(
        "DO $$ BEGIN CREATE TYPE path_item_type AS ENUM ('SKILL', 'PROJECT', 'SECTION'); EXCEPTION WHEN duplicate_object THEN null; END $$"
    )

    # learning_path_items
    op.create_table(
        "learning_path_items",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "path_id",
            sa.String(26),
            sa.ForeignKey("learning_paths.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_type",
            PGENUM("SKILL", "PROJECT", "SECTION", name="path_item_type", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "skill_id", sa.String(26), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column(
            "project_id",
            sa.String(26),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("section_title", sa.String(200), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("unlock_rule", sa.String(30), nullable=False, server_default="previous_required"),
        sa.CheckConstraint(
            "(item_type = 'SKILL' AND skill_id IS NOT NULL) OR "
            "(item_type = 'PROJECT' AND project_id IS NOT NULL) OR "
            "(item_type = 'SECTION' AND section_title IS NOT NULL)",
            name="ck_path_item_type_ref",
        ),
    )
    op.create_index("ix_path_items_order", "learning_path_items", ["path_id", "sort_order"])

    # cohort_learning_path_assignments (composite PK)
    op.create_table(
        "cohort_learning_path_assignments",
        sa.Column(
            "cohort_id",
            sa.String(26),
            sa.ForeignKey("cohorts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "path_id",
            sa.String(26),
            sa.ForeignKey("learning_paths.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("assigned_by", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cohort_learning_path_assignments")
    op.drop_index("ix_path_items_order", "learning_path_items")
    op.drop_table("learning_path_items")
    op.drop_index("ix_paths_org_status", "learning_paths")
    op.drop_index("uq_path_org_slug", "learning_paths")
    op.drop_table("learning_paths")
    op.execute("DROP TYPE IF EXISTS path_item_type")
