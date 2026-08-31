"""Control plane: client portal (members, guest links, approvals, shares)
+ submission_comments client-visibility columns (Issue #27, ADR-014 §9).

Revision ID: cp09c0000009
Revises: cp08b0000008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cp09c0000009"
down_revision: str | None = "cp08b0000008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_client_portal_members",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(26),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="active"),
        sa.Column(
            "invited_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_portal_member", "cp_client_portal_members", ["project_id", "user_id"], unique=True
    )
    op.create_index("ix_cp_portal_members_user", "cp_client_portal_members", ["user_id"])
    op.create_table(
        "cp_client_guest_links",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(26),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cp_guest_links_project", "cp_client_guest_links", ["project_id"])
    op.create_table(
        "cp_client_approvals",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(26),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "submission_id",
            sa.String(26),
            sa.ForeignKey("submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("acted_by_user_id", sa.String(26), nullable=True),
        sa.Column("acted_by_link_id", sa.String(26), nullable=True),
        sa.Column("acted_by_label", sa.String(200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cp_approvals_project", "cp_client_approvals", ["project_id", "created_at"])
    op.create_index("ix_cp_approvals_submission", "cp_client_approvals", ["submission_id"])
    op.create_index(
        "uq_cp_final_accept",
        "cp_client_approvals",
        ["project_id"],
        unique=True,
        postgresql_where=sa.text("action = 'final_accepted'"),
    )
    op.create_table(
        "cp_client_shares",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(26),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "submission_id",
            sa.String(26),
            sa.ForeignKey("submissions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "shared_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("note", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    # submission_comments: guests have no user row; internal comments are
    # hidden from the portal by default.
    op.alter_column("submission_comments", "author_id", nullable=True)
    op.add_column(
        "submission_comments",
        sa.Column("client_visible", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "submission_comments",
        sa.Column("client_author_label", sa.String(200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("submission_comments", "client_author_label")
    op.drop_column("submission_comments", "client_visible")
    op.alter_column("submission_comments", "author_id", nullable=False)
    op.drop_table("cp_client_shares")
    op.drop_table("cp_client_approvals")
    op.drop_table("cp_client_guest_links")
    op.drop_table("cp_client_portal_members")
