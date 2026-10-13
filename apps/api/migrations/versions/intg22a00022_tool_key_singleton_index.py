"""R422: enforce the LTI tool-key singleton the code already assumes.

ensure_tool_key's concurrent-first-use recovery (R111) is written against a
"singleton index arbitrates" contract, but no such index ever existed — kid
is random and never collides, so in a true cold-start race BOTH sessions
insert and the environment ends up with two active signing keys (and the
IntegrityError recovery branch is dead code). Add the partial unique index;
first deactivate all but the newest active key so the index can build on
any environment that already raced into duplicates.

Revision ID: intg22a00022
Revises: intg21a00021
Create Date: 2026-10-14
"""

from alembic import op

revision = "intg22a00022"
down_revision = "intg21a00021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep only the newest active key (created_at then id — ULIDs are
    # time-ordered, so id breaks created_at ties deterministically).
    op.execute(
        """
        UPDATE intg_lti_tool_keys SET active = false
        WHERE active AND id <> (
            SELECT id FROM intg_lti_tool_keys WHERE active
            ORDER BY created_at DESC, id DESC LIMIT 1
        )
        """
    )
    op.create_index(
        "uq_intg_lti_tool_key_active",
        "intg_lti_tool_keys",
        ["active"],
        unique=True,
        postgresql_where="active",
    )


def downgrade() -> None:
    op.drop_index("uq_intg_lti_tool_key_active", table_name="intg_lti_tool_keys")
