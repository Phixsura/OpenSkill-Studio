"""F3-F10 features: notifications, pack_categories, certificates, review_status

Revision ID: b2c3d4e5f607
Revises: a1b2c3d4e5f6
Create Date: 2026-08-20 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f607"
down_revision: str | None = "e5f607182930"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── notifications ──
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("data", JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_notifications_user_unread",
        "notifications",
        ["user_id", "is_read"],
    )
    op.create_index(
        "ix_notifications_user_created",
        "notifications",
        ["user_id", "created_at"],
    )

    # ── pack_categories ──
    op.create_table(
        "pack_categories",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column(
            "parent_id",
            sa.String(26),
            sa.ForeignKey("pack_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index(
        "uq_pack_category_slug",
        "pack_categories",
        ["slug"],
        unique=True,
    )

    # ── pack_category_assignments ──
    op.create_table(
        "pack_category_assignments",
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("skill_packs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "category_id",
            sa.String(26),
            sa.ForeignKey("pack_categories.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # ── certificates ──
    op.create_table(
        "certificates",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "path_id",
            sa.String(26),
            sa.ForeignKey("learning_paths.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("certificate_number", sa.String(36), nullable=False, unique=True),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("data", JSONB(), nullable=False, server_default="{}"),
    )
    op.create_index(
        "uq_certificate_number",
        "certificates",
        ["certificate_number"],
        unique=True,
    )
    op.create_index(
        "ix_certificates_user_path",
        "certificates",
        ["user_id", "path_id"],
    )

    # ── ALTER skill_packs ADD review_status ──
    op.add_column(
        "skill_packs",
        sa.Column("review_status", sa.String(20), nullable=True),
    )

    # ── Seed default pack categories ──
    from ulid import ULID

    categories = [
        ("AI & ML", "ai-ml", "brain", 0),
        ("Design", "design", "palette", 1),
        ("Development", "development", "code", 2),
        ("Business", "business", "briefcase", 3),
        ("Marketing", "marketing", "megaphone", 4),
    ]
    for name, slug, icon, sort_order in categories:
        op.execute(
            sa.text(
                "INSERT INTO pack_categories (id, name, slug, icon, sort_order) "
                "VALUES (:id, :name, :slug, :icon, :sort_order)"
            ).bindparams(
                id=str(ULID()),
                name=name,
                slug=slug,
                icon=icon,
                sort_order=sort_order,
            )
        )


def downgrade() -> None:
    op.drop_column("skill_packs", "review_status")
    op.drop_index("ix_certificates_user_path", table_name="certificates")
    op.drop_index("uq_certificate_number", table_name="certificates")
    op.drop_table("certificates")
    op.drop_table("pack_category_assignments")
    op.drop_index("uq_pack_category_slug", table_name="pack_categories")
    op.drop_table("pack_categories")
    op.drop_index("ix_notifications_user_created", table_name="notifications")
    op.drop_index("ix_notifications_user_unread", table_name="notifications")
    op.drop_table("notifications")
