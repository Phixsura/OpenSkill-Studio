"""talent07: employer branding + candidate notes

Revision ID: talent07a00007
Revises: talent06a00006
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "talent07a00007"
down_revision = "talent06a00006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Employer branding fields (I6)
    op.add_column(
        "employer_profiles",
        sa.Column("cover_image_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "employer_profiles",
        sa.Column("culture_text", sa.Text, nullable=True),
    )
    op.add_column(
        "employer_profiles",
        sa.Column(
            "benefits",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "employer_profiles",
        sa.Column(
            "values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "employer_profiles",
        sa.Column(
            "social_links",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    # Candidate notes table (N4)
    op.create_table(
        "talent_candidate_notes",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "candidate_user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "author_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "opportunity_id",
            sa.String(26),
            sa.ForeignKey("opportunities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("note_text", sa.Text, nullable=False),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_candidate_notes_org_user",
        "talent_candidate_notes",
        ["org_id", "candidate_user_id"],
    )
    op.create_index(
        "ix_candidate_notes_author",
        "talent_candidate_notes",
        ["author_id"],
    )


def downgrade() -> None:
    op.drop_table("talent_candidate_notes")
    op.drop_column("employer_profiles", "social_links")
    op.drop_column("employer_profiles", "values")
    op.drop_column("employer_profiles", "benefits")
    op.drop_column("employer_profiles", "culture_text")
    op.drop_column("employer_profiles", "cover_image_url")
