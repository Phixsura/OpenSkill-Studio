"""skill_packs — 5 new tables for versioned content distribution

Revision ID: 102e6638eaa1
Revises: f34d9c53f007
Create Date: 2026-08-19 12:05:47.709270
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "102e6638eaa1"
down_revision: str | None = "f34d9c53f007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums are created by SQLAlchemy model metadata when Alembic loads.
    # The sa.Enum columns below use create_type=False to avoid duplicate creation.

    # skill_packs
    op.create_table(
        "skill_packs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "owner_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("summary", sa.String(500), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PUBLISHED",
                "ARCHIVED",
                name="pack_status",
                create_constraint=False,
                create_type=False,
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column(
            "visibility",
            sa.Enum(
                "PRIVATE",
                "UNLISTED",
                "PUBLIC",
                name="pack_visibility",
                create_constraint=False,
                create_type=False,
            ),
            nullable=False,
            server_default="PRIVATE",
        ),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("cover_image_key", sa.String(500), nullable=True),
        sa.Column("learning_outcomes", JSONB(), nullable=False, server_default="[]"),
        sa.Column("scenario_tags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("tool_tags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("capability_tags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("prerequisite_packs", JSONB(), nullable=False, server_default="[]"),
        sa.Column("install_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provenance", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_pack_org_slug", "skill_packs", ["owner_org_id", "slug"], unique=True)
    op.create_index("ix_packs_visibility_status", "skill_packs", ["visibility", "status"])
    op.create_index("ix_packs_owner", "skill_packs", ["owner_org_id"])

    # skill_pack_skills (composite PK)
    op.create_table(
        "skill_pack_skills",
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("skill_packs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "skill_id",
            sa.String(26),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )

    # skill_pack_templates (composite PK)
    op.create_table(
        "skill_pack_templates",
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("skill_packs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "template_id",
            sa.String(26),
            sa.ForeignKey("project_templates.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )

    # skill_pack_releases
    op.create_table(
        "skill_pack_releases",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("skill_packs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("manifest", JSONB(), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("component_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("released_by", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_release_version", "skill_pack_releases", ["pack_id", "version"], unique=True
    )
    op.create_index("ix_releases_pack_date", "skill_pack_releases", ["pack_id", "released_at"])

    # skill_pack_installations
    op.create_table(
        "skill_pack_installations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("skill_packs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "release_id",
            sa.String(26),
            sa.ForeignKey("skill_pack_releases.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("installed_version", sa.String(20), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "FORKED",
                "REMOVED",
                name="install_status",
                create_constraint=False,
                create_type=False,
            ),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("installed_by", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_install_org_pack", "skill_pack_installations", ["org_id", "pack_id"], unique=True
    )
    op.create_index("ix_installs_org", "skill_pack_installations", ["org_id"])


def downgrade() -> None:
    op.drop_index("ix_installs_org", "skill_pack_installations")
    op.drop_index("uq_install_org_pack", "skill_pack_installations")
    op.drop_table("skill_pack_installations")

    op.drop_index("ix_releases_pack_date", "skill_pack_releases")
    op.drop_index("uq_release_version", "skill_pack_releases")
    op.drop_table("skill_pack_releases")

    op.drop_table("skill_pack_templates")
    op.drop_table("skill_pack_skills")

    op.drop_index("ix_packs_owner", "skill_packs")
    op.drop_index("ix_packs_visibility_status", "skill_packs")
    op.drop_index("uq_pack_org_slug", "skill_packs")
    op.drop_table("skill_packs")

    op.execute("DROP TYPE IF EXISTS install_status")
    op.execute("DROP TYPE IF EXISTS pack_visibility")
    op.execute("DROP TYPE IF EXISTS pack_status")
