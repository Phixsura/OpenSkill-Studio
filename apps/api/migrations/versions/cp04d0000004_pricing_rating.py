"""Control plane: cost rates, price policies, rated usage, FX, reconciliation
+ seed the global cost+50% fallback policy (Issue #27, ADR-014 §4).

Revision ID: cp04d0000004
Revises: cp03c0000003
"""

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from ulid import ULID

revision: str = "cp04d0000004"
down_revision: str | None = "cp03c0000003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_provider_cost_rates",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model_or_service", sa.String(200), nullable=True),
        sa.Column("usage_type", sa.String(40), nullable=False),
        sa.Column("capability_key", sa.String(64), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 8), nullable=False),
        sa.Column("tier_rules", JSONB(), nullable=True),
        sa.Column("minimum_fee_minor", sa.BigInteger(), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_note", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_cp_cost_rates_lookup",
        "cp_provider_cost_rates",
        ["provider", "model_or_service", "usage_type", "effective_from"],
    )
    op.create_table(
        "cp_price_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("policy_type", sa.String(40), nullable=False),
        sa.Column("usage_type", sa.String(40), nullable=True),
        sa.Column("capability_key", sa.String(64), nullable=True),
        sa.Column("plan_version_id", sa.String(26), nullable=True),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("params", JSONB(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_cp_policies_tenant", "cp_price_policies", ["tenant_id", "usage_type", "effective_from"]
    )
    op.create_index("ix_cp_policies_plan", "cp_price_policies", ["plan_version_id", "usage_type"])
    op.create_table(
        "cp_rated_usage",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("usage_event_id", sa.String(26), nullable=False),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("usage_type", sa.String(40), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("cost_rate_id", sa.String(26), nullable=True),
        sa.Column("cost_rate_snapshot", JSONB(), nullable=False),
        sa.Column("internal_cost_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("internal_cost_currency", sa.String(3), nullable=False),
        sa.Column("price_policy_id", sa.String(26), nullable=True),
        sa.Column("sell_rate_snapshot", JSONB(), nullable=False),
        sa.Column("billable_amount_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("billable_currency", sa.String(3), nullable=False),
        sa.Column("fx_rate_snapshot", JSONB(), nullable=True),
        sa.Column("margin_minor", sa.BigInteger(), nullable=True),
        sa.Column("rating_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(12), nullable=False, server_default="rated"),
        sa.Column("invoice_line_id", sa.String(26), nullable=True),
        sa.Column("void_reason", sa.String(500), nullable=True),
        sa.Column(
            "rated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("uq_cp_rated_event", "cp_rated_usage", ["usage_event_id"], unique=True)
    op.create_index("ix_cp_rated_tenant_time", "cp_rated_usage", ["tenant_id", "rated_at"])
    op.create_index("ix_cp_rated_status_tenant", "cp_rated_usage", ["status", "tenant_id"])
    op.create_index(
        "ix_cp_rated_blocked",
        "cp_rated_usage",
        ["status"],
        postgresql_where=sa.text("status = 'blocked'"),
    )
    op.create_table(
        "cp_fx_rates",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("base_currency", sa.String(3), nullable=False),
        sa.Column("quote_currency", sa.String(3), nullable=False),
        sa.Column("rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_cp_fx_pair", "cp_fx_rates", ["base_currency", "quote_currency", "effective_from"]
    )
    op.create_table(
        "cp_reconciliation_reports",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model_or_service", sa.String(200), nullable=True),
        sa.Column("usage_type", sa.String(40), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("provider_reported_quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("provider_reported_cost_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("platform_quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("platform_cost_minor", sa.BigInteger(), nullable=False),
        sa.Column("delta_quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("delta_cost_minor", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="open"),
        sa.Column("note", sa.String(500), nullable=True),
        sa.Column("resolved_note", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Seed: global cost+50% fallback policy (user decision — platform bills
    # something sensible out of the box; ops override with specific policies).
    bind = op.get_bind()
    exists = bind.execute(
        sa.text("SELECT id FROM cp_price_policies WHERE name = 'Global default (cost + 50%)'")
    ).fetchone()
    if not exists:
        bind.execute(
            sa.text(
                "INSERT INTO cp_price_policies "
                "(id, name, policy_type, currency, params, priority, effective_from, is_active, created_at) "
                "VALUES (:id, 'Global default (cost + 50%)', 'cost_plus_percentage', 'USD', "
                ":params, -1000, '2020-01-01T00:00:00Z', true, now())"
            ),
            {"id": str(ULID()), "params": json.dumps({"percentage": "50"})},
        )


def downgrade() -> None:
    op.drop_table("cp_reconciliation_reports")
    op.drop_table("cp_fx_rates")
    op.drop_table("cp_rated_usage")
    op.drop_table("cp_price_policies")
    op.drop_table("cp_provider_cost_rates")
