"""R572: repo-wide drift audit fixes —

skill_passports.alumni_mode had a model column but NO migration:
every ORM SELECT of SkillPassport failed with UndefinedColumnError on a
migrated database (production-dead passport surface). Also: two talent
scorecard columns were JSONB in the model but JSON in the database (the
models' containment/index semantics silently unavailable). These are the
only missing-column / wrong-type drifts in the repo.

Revision ID: intg26a00026
Revises: intg25a00025
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "intg26a00026"
down_revision = "intg25a00025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "skill_passports",
        sa.Column("alumni_mode", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.alter_column(
        "talent_interview_scorecards",
        "ratings",
        type_=postgresql.JSONB(),
        postgresql_using="ratings::jsonb",
    )
    op.alter_column(
        "talent_scorecard_templates",
        "criteria",
        type_=postgresql.JSONB(),
        postgresql_using="criteria::jsonb",
    )


def downgrade() -> None:
    op.alter_column(
        "talent_scorecard_templates", "criteria", type_=sa.JSON(), postgresql_using="criteria::json"
    )
    op.alter_column(
        "talent_interview_scorecards", "ratings", type_=sa.JSON(), postgresql_using="ratings::json"
    )
    op.drop_column("skill_passports", "alumni_mode")
