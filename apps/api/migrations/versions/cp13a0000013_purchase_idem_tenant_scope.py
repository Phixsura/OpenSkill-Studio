"""Control plane: scope purchase idempotency uniqueness to (buyer_tenant, key)

R72: uq_cp_purchase_idem was unique on idempotency_key alone — a global
namespace for client-supplied keys. The same key on two different buyer
tenants matched the FIRST tenant's purchase (cross-tenant data leak; the
credit path then debited the wrong tenant's balance) or tripped the unique
index. Idempotency keys are per-buyer, so the uniqueness must be too.

Revision ID: cp13a0000013
Revises: cp12f0000012
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cp13a0000013"
down_revision: str | None = "cp12f0000012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("uq_cp_purchase_idem", table_name="cp_marketplace_purchases")
    op.create_index(
        "uq_cp_purchase_idem",
        "cp_marketplace_purchases",
        ["buyer_tenant_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_cp_purchase_idem", table_name="cp_marketplace_purchases")
    op.create_index(
        "uq_cp_purchase_idem",
        "cp_marketplace_purchases",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
