"""R135: credit-note idempotency.

Adds cp_credit_notes.idempotency_key + a partial unique index per invoice —
a retried POST created a second note and double-refunded the ledger (each
retry minted a fresh cn:{new_note_id} refund key, so the ledger dedup could
never fire).

Revision ID: cp22c0000022
Revises: cp21c0000021
"""

import sqlalchemy as sa
from alembic import op

revision = "cp22c0000022"
down_revision = "cp21c0000021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cp_credit_notes",
        sa.Column("idempotency_key", sa.String(120), nullable=True),
    )
    op.create_index(
        "uq_cp_credit_note_idem",
        "cp_credit_notes",
        ["invoice_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_cp_credit_note_idem", table_name="cp_credit_notes")
    op.drop_column("cp_credit_notes", "idempotency_key")
