"""Control plane: scope credit-ledger idempotency uniqueness to (tenant, key)

R51: uq_cp_credit_idem was unique on idempotency_key alone — a global
namespace. A client-supplied key on POST /platform/tenants/{id}/credits/adjust
(the only raw, un-prefixed key path) collided across tenants: the same key on
tenant B matched tenant A's entry (sequential → silently dropped) or tripped
the unique index (concurrent → 500). Idempotency keys are per-tenant, so the
uniqueness must be too.

Revision ID: cp11e0000011
Revises: cp10d0000010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cp11e0000011"
down_revision: str | None = "cp10d0000010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("uq_cp_credit_idem", table_name="cp_credit_ledger")
    op.create_index(
        "uq_cp_credit_idem",
        "cp_credit_ledger",
        ["tenant_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_cp_credit_idem", table_name="cp_credit_ledger")
    op.create_index(
        "uq_cp_credit_idem",
        "cp_credit_ledger",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
