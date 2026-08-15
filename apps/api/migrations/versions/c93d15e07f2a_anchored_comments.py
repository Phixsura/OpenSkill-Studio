"""anchored submission comments (Frame.io-style global/time/region anchors)

Revision ID: c93d15e07f2a
Revises: b71f22c04d1e
Create Date: 2026-08-15
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "c93d15e07f2a"
down_revision = "b71f22c04d1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    comment_anchor = postgresql.ENUM(
        "GLOBAL", "TIME", "REGION", name="comment_anchor_type", create_type=False
    )
    comment_anchor.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "submission_comments",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("submission_id", sa.String(26), nullable=False),
        sa.Column("item_id", sa.String(26), nullable=False),
        sa.Column("author_id", sa.String(26), nullable=False),
        sa.Column("parent_id", sa.String(26), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("anchor_type", comment_anchor, nullable=False),
        sa.Column("timestamp_ms", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("region", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["submission_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["submission_comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_item_created", "submission_comments", ["item_id", "created_at"])
    op.create_index("ix_comments_submission", "submission_comments", ["submission_id"])


def downgrade() -> None:
    op.drop_index("ix_comments_submission", table_name="submission_comments")
    op.drop_index("ix_comments_item_created", table_name="submission_comments")
    op.drop_table("submission_comments")
    postgresql.ENUM(name="comment_anchor_type").drop(op.get_bind(), checkfirst=True)
