"""talent10: credential pathways + career goals

Revision ID: talent10a00010
Revises: talent09a00009
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "talent10a00010"
down_revision = "talent09a00009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Credential Pathways (N2)
    op.create_table(
        "talent_credential_pathways",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("pathway_credential_type", sa.String(100), nullable=False),
        sa.Column("prerequisite_credential_types", JSONB, nullable=False, server_default="[]"),
        sa.Column("prerequisite_count", sa.Integer, nullable=False),
        sa.Column("auto_issue", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("status", sa.String(20), nullable=False, server_default="'active'"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_talent_cred_pathways_org", "talent_credential_pathways", ["org_id"])
    op.create_index("ix_talent_cred_pathways_status", "talent_credential_pathways", ["status"])

    # Career Goals (N3)
    op.create_table(
        "talent_career_goals",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target_role", sa.String(200), nullable=True),
        sa.Column("target_capabilities", JSONB, nullable=False, server_default="[]"),
        sa.Column("target_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="'active'"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_talent_career_goals_user", "talent_career_goals", ["user_id"])
    op.create_index("ix_talent_career_goals_status", "talent_career_goals", ["user_id", "status"])


# NOTE: downgrade drops tables — run in order
def downgrade() -> None:
    op.drop_table("talent_career_goals")
    op.drop_table("talent_credential_pathways")
