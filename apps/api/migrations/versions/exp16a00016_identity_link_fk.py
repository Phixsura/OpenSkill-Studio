"""identity links cascade with user deletion (ADR-017 §4.17, round 222)

The anon↔user mapping is privacy-relevant: deleting the user must not
orphan it.

Revision ID: exp16a00016
Revises: exp15a00015
Create Date: 2026-10-05
"""

from alembic import op

revision = "exp16a00016"
down_revision = "exp15a00015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_experiment_identity_links_user",
        "experiment_identity_links",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_experiment_identity_links_user",
        "experiment_identity_links",
        type_="foreignkey",
    )
