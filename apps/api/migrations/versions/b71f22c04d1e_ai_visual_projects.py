"""ai visual projects: media deliverable types, templates, assets, item versioning

Revision ID: b71f22c04d1e
Revises: 8ecac13ada9e
Create Date: 2026-08-15
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b71f22c04d1e"
down_revision = "8ecac13ada9e"
branch_labels = None
depends_on = None

NEW_DELIVERABLE_VALUES = ("IMAGE", "VIDEO", "AUDIO", "PROMPT", "REFERENCE", "FINAL_OUTPUT")


def upgrade() -> None:
    # PG cannot ADD VALUE to an enum inside a transaction block
    with op.get_context().autocommit_block():
        for value in NEW_DELIVERABLE_VALUES:
            op.execute(f"ALTER TYPE deliverable_type ADD VALUE IF NOT EXISTS '{value}'")
        op.execute("ALTER TYPE item_type ADD VALUE IF NOT EXISTS 'PROMPT'")

    # The initial schema created enums with CHECK constraints — widen them
    op.execute("ALTER TABLE project_deliverables DROP CONSTRAINT IF EXISTS deliverable_type")
    op.execute("ALTER TABLE submission_items DROP CONSTRAINT IF EXISTS item_type")

    op.add_column(
        "projects",
        sa.Column("project_type", sa.String(20), server_default="general", nullable=False),
    )
    op.add_column(
        "submission_items",
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
    )
    op.add_column("submission_items", sa.Column("note", sa.Text(), nullable=True))
    op.add_column("submission_items", sa.Column("uploaded_by", sa.String(26), nullable=True))
    op.create_foreign_key(
        "fk_submission_items_uploaded_by",
        "submission_items",
        "users",
        ["uploaded_by"],
        ["id"],
    )

    op.create_table(
        "project_templates",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("project_type", sa.String(20), server_default="general", nullable=False),
        sa.Column(
            "difficulty",
            postgresql.ENUM(name="difficulty_level", create_type=False),
            nullable=False,
        ),
        sa.Column("suggested_minutes", sa.Integer(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("rubric", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "deliverables",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "skill_names",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(name="content_status", create_type=False),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_templates_org_status", "project_templates", ["org_id", "status"])

    op.create_table(
        "project_assets",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("project_id", sa.String(26), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.String(26), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_project_order", "project_assets", ["project_id", "sort_order"])


def downgrade() -> None:
    op.drop_index("ix_assets_project_order", table_name="project_assets")
    op.drop_table("project_assets")
    op.drop_index("ix_templates_org_status", table_name="project_templates")
    op.drop_table("project_templates")
    op.drop_constraint("fk_submission_items_uploaded_by", "submission_items", type_="foreignkey")
    op.drop_column("submission_items", "uploaded_by")
    op.drop_column("submission_items", "note")
    op.drop_column("submission_items", "version")
    op.drop_column("projects", "project_type")
    # PG enums cannot remove values — leave the extra values in place (harmless)
