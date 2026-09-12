"""Control plane: credit balances/ledger/reservations + budget policies
(Issue #27, ADR-014 §5).

Revision ID: cp05e0000005
Revises: cp04d0000004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "cp05e0000005"
down_revision: str | None = "cp04d0000004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_credit_balances",
        sa.Column("tenant_id", sa.String(26), primary_key=True),
        sa.Column("currency", sa.String(3), primary_key=True),
        sa.Column("balance_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("reserved_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "balance_minor >= 0 AND reserved_minor >= 0 AND balance_minor >= reserved_minor",
            name="ck_cp_balance_nonneg",
        ),
    )
    op.create_table(
        "cp_credit_ledger",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("entry_type", sa.String(20), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("balance_after_minor", sa.BigInteger(), nullable=False),
        sa.Column("reference_type", sa.String(30), nullable=True),
        sa.Column("reference_id", sa.String(120), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_expiration_id", sa.String(26), nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_credit_idem",
        "cp_credit_ledger",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_index(
        "ix_cp_credit_tenant_time", "cp_credit_ledger", ["tenant_id", "currency", "created_at"]
    )
    op.create_index(
        "ix_cp_credit_promo",
        "cp_credit_ledger",
        ["tenant_id"],
        postgresql_where=sa.text("entry_type = 'promotional'"),
    )
    op.create_table(
        "cp_credit_reservations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="held"),
        sa.Column("reference_type", sa.String(30), nullable=False),
        sa.Column("reference_id", sa.String(120), nullable=False),
        sa.Column("settled_amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("extension_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_cp_reservation_held",
        "cp_credit_reservations",
        ["reference_type", "reference_id"],
        unique=True,
        postgresql_where=sa.text("status = 'held'"),
    )
    op.create_index("ix_cp_reservations_expiry", "cp_credit_reservations", ["status", "expires_at"])
    op.create_index("ix_cp_reservations_tenant", "cp_credit_reservations", ["tenant_id"])
    op.create_table(
        "cp_budget_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("scope_type", sa.String(10), nullable=False),
        sa.Column("scope_id", sa.String(26), nullable=True),
        sa.Column("period", sa.String(10), nullable=False),
        sa.Column("capability_key", sa.String(64), nullable=True),
        sa.Column("usage_type", sa.String(40), nullable=True),
        sa.Column("limit_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("warning_threshold_pct", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("hard_stop", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_cp_budget_dims ON cp_budget_policies "
        "(tenant_id, scope_type, coalesce(scope_id, ''), period, "
        "coalesce(capability_key, ''), coalesce(usage_type, ''))"
    )
    op.create_index("ix_cp_budgets_tenant", "cp_budget_policies", ["tenant_id", "is_active"])

    # Convert legacy org eval budgets (settings.ai_evaluation.monthly_budget_usd)
    # into BudgetPolicy rows — issue §17 "one budget system".
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            "SELECT id, tenant_id, (settings->'ai_evaluation'->>'monthly_budget_usd') AS budget "
            "FROM organizations "
            "WHERE settings->'ai_evaluation' ? 'monthly_budget_usd' "
            "AND jsonb_typeof(settings->'ai_evaluation'->'monthly_budget_usd') = 'number'"
        )
    ).fetchall()
    from ulid import ULID

    for row in rows:
        try:
            limit_minor = int(float(row.budget) * 100)
        except (TypeError, ValueError, OverflowError):
            continue
        # R93[m3]: jsonb numerics are arbitrary-precision — a historical
        # budget of 1e20 converted to a limit_minor beyond BIGINT and the
        # INSERT crashed the ENTIRE upgrade (asyncpg DataError, out of range
        # for int8). Clamp to the int8-safe money ceiling; a nonsensical
        # legacy value becomes a very-large-but-valid cap instead of a
        # deploy-blocking migration failure.
        limit_minor = min(limit_minor, 1_000_000_000_000_000)  # 10^15
        if limit_minor <= 0:
            continue
        bind.execute(
            sa.text(
                "INSERT INTO cp_budget_policies "
                "(id, tenant_id, scope_type, scope_id, period, limit_minor, currency, "
                " hard_stop, is_active, metadata, created_at, updated_at) "
                "VALUES (:id, :tid, 'org', :oid, 'monthly', :lim, 'USD', true, true, "
                ' \'{"source": "eval_settings_migration"}\', now(), now()) '
                "ON CONFLICT DO NOTHING"
            ),
            {"id": str(ULID()), "tid": row.tenant_id, "oid": row.id, "lim": limit_minor},
        )


def downgrade() -> None:
    op.drop_table("cp_budget_policies")
    op.drop_table("cp_credit_reservations")
    op.drop_table("cp_credit_ledger")
    op.drop_table("cp_credit_balances")
