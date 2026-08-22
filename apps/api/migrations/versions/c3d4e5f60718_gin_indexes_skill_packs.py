"""Add GIN indexes for JSONB tag columns on skill_packs

Revision ID: c3d4e5f60718
Revises: 10fbb2faf2d0
Create Date: 2026-08-20
"""

from alembic import op

revision: str = "c3d4e5f60718"
down_revision: str | None = "10fbb2faf2d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX ix_skill_packs_scenario_tags ON skill_packs USING GIN (scenario_tags)"
    )
    op.execute(
        "CREATE INDEX ix_skill_packs_tool_tags ON skill_packs USING GIN (tool_tags)"
    )
    op.execute(
        "CREATE INDEX ix_skill_packs_capability_tags ON skill_packs USING GIN (capability_tags)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_skill_packs_capability_tags")
    op.execute("DROP INDEX IF EXISTS ix_skill_packs_tool_tags")
    op.execute("DROP INDEX IF EXISTS ix_skill_packs_scenario_tags")
