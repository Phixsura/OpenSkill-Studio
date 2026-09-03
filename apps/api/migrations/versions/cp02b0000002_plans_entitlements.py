"""Control plane: plans, plan versions, prices, entitlement overrides + seed
5 plans (v1 ACTIVE) + convert grandfather metadata into override rows
(Issue #27, ADR-014 §2).

Revision ID: cp02b0000002
Revises: cp01a0000001
"""

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from ulid import ULID

revision: str = "cp02b0000002"
down_revision: str | None = "cp01a0000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_product_plans",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "cp_plan_versions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "plan_id",
            sa.String(26),
            sa.ForeignKey("cp_product_plans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="draft"),
        sa.Column("entitlements", JSONB(), nullable=False, server_default="{}"),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("uq_cp_plan_version", "cp_plan_versions", ["plan_id", "version"], unique=True)
    op.create_index(
        "uq_cp_plan_active",
        "cp_plan_versions",
        ["plan_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_table(
        "cp_plan_prices",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "plan_version_id",
            sa.String(26),
            sa.ForeignKey("cp_plan_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("interval", sa.String(10), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("included_seats", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overage_seat_amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("external_price_ref", sa.String(100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_plan_price",
        "cp_plan_prices",
        ["plan_version_id", "currency", "interval"],
        unique=True,
    )
    op.create_table(
        "cp_entitlement_overrides",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(26),
            sa.ForeignKey("cp_tenant_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String(60), nullable=False),
        sa.Column("value", JSONB(), nullable=False),
        sa.Column("enforcement", sa.String(10), nullable=False, server_default="hard"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_ent_override", "cp_entitlement_overrides", ["tenant_id", "key"], unique=True
    )

    # ── Seed: 5 plans × v1 ACTIVE + prices (upsert-by-key, rerunnable) ──
    bind = op.get_bind()
    # (key, name, sort, entitlements, monthly_minor, included_seats, seat_overage_minor)
    seats_overage = 500  # $5.00 per seat over included
    plans = [
        (
            "community",
            "Community",
            0,
            {
                "max_organizations": 1,
                "max_active_learners": 25,
                "max_instructors": 3,
                "max_storage_gb": "5",
                "max_ai_budget_usd_month": None,
                "max_workflow_runs_month": 100,
                "max_api_requests_day": 10000,
                "custom_domain": False,
                "white_label": False,
                "client_portal": False,
                "private_registry": True,
                "paid_marketplace": False,
                "advanced_analytics": False,
                "webhooks": True,
                "api_access": True,
            },
            0,
            25,
        ),
        (
            "school",
            "School",
            1,
            {
                "max_organizations": 3,
                "max_active_learners": 200,
                "max_instructors": 15,
                "max_storage_gb": "50",
                "max_ai_budget_usd_month": "500",
                "max_workflow_runs_month": 1000,
                "max_api_requests_day": 50000,
                "custom_domain": True,
                "white_label": False,
                "client_portal": True,
                "private_registry": True,
                "paid_marketplace": False,
                "advanced_analytics": True,
                "webhooks": True,
                "api_access": True,
            },
            19900,
            200,
        ),
        (
            "growth",
            "Growth Center",
            2,
            {
                "max_organizations": 10,
                "max_active_learners": 1000,
                "max_instructors": 50,
                "max_storage_gb": "200",
                "max_ai_budget_usd_month": "2000",
                "max_workflow_runs_month": 5000,
                "max_api_requests_day": 200000,
                "custom_domain": True,
                "white_label": True,
                "client_portal": True,
                "private_registry": True,
                "paid_marketplace": True,
                "advanced_analytics": True,
                "webhooks": True,
                "api_access": True,
            },
            49900,
            1000,
        ),
        (
            "enterprise",
            "Enterprise",
            3,
            {
                "max_organizations": None,
                "max_active_learners": None,
                "max_instructors": None,
                "max_storage_gb": "1000",
                "max_ai_budget_usd_month": None,
                "max_workflow_runs_month": None,
                "max_api_requests_day": 1000000,
                "custom_domain": True,
                "white_label": True,
                "client_portal": True,
                "private_registry": True,
                "paid_marketplace": True,
                "advanced_analytics": True,
                "webhooks": True,
                "api_access": True,
            },
            199900,
            0,
        ),
        (
            "oem",
            "OEM",
            4,
            {
                "max_organizations": None,
                "max_active_learners": None,
                "max_instructors": None,
                "max_storage_gb": "2000",
                "max_ai_budget_usd_month": None,
                "max_workflow_runs_month": None,
                "max_api_requests_day": 2000000,
                "custom_domain": True,
                "white_label": True,
                "client_portal": True,
                "private_registry": True,
                "paid_marketplace": True,
                "advanced_analytics": True,
                "webhooks": True,
                "api_access": True,
            },
            499900,
            0,
        ),
    ]
    for key, name, sort, ents, monthly_minor, included_seats in plans:
        exists = bind.execute(
            sa.text("SELECT id FROM cp_product_plans WHERE key = :k"), {"k": key}
        ).fetchone()
        if exists:
            continue
        plan_id = str(ULID())
        bind.execute(
            sa.text(
                "INSERT INTO cp_product_plans (id, key, name, is_active, sort_order, created_at, updated_at) "
                "VALUES (:id, :key, :name, true, :sort, now(), now())"
            ),
            {"id": plan_id, "key": key, "name": name, "sort": sort},
        )
        version_id = str(ULID())
        bind.execute(
            sa.text(
                "INSERT INTO cp_plan_versions (id, plan_id, version, status, entitlements, activated_at, created_at) "
                "VALUES (:id, :pid, 1, 'active', :ents, now(), now())"
            ),
            {"id": version_id, "pid": plan_id, "ents": json.dumps(ents)},
        )
        for currency, interval, amount in [
            ("USD", "month", monthly_minor),
            ("USD", "year", monthly_minor * 10),
        ]:
            bind.execute(
                sa.text(
                    "INSERT INTO cp_plan_prices (id, plan_version_id, currency, interval, amount_minor, included_seats, overage_seat_amount_minor, created_at) "
                    "VALUES (:id, :vid, :cur, :iv, :amt, :seats, :ovg, now())"
                ),
                {
                    "id": str(ULID()),
                    "vid": version_id,
                    "cur": currency,
                    "iv": interval,
                    "amt": amount,
                    "seats": included_seats,
                    "ovg": seats_overage if included_seats else None,
                },
            )

    # ── Convert grandfather metadata (from cp01 backfill) into override rows ──
    rows = bind.execute(
        sa.text(
            "SELECT id, metadata FROM cp_tenant_accounts WHERE metadata ? 'grandfather_overrides'"
        )
    ).fetchall()
    for row in rows:
        overrides = (row.metadata or {}).get("grandfather_overrides", {})
        for key, value in overrides.items():
            bind.execute(
                sa.text(
                    "INSERT INTO cp_entitlement_overrides "
                    "(id, tenant_id, key, value, enforcement, reason, created_at, updated_at) "
                    "VALUES (:id, :tid, :key, :val, 'hard', 'migration grandfathering', now(), now()) "
                    "ON CONFLICT DO NOTHING"
                ),
                {
                    "id": str(ULID()),
                    "tid": row.id,
                    "key": key,
                    "val": json.dumps({"v": value}),
                },
            )
        bind.execute(
            sa.text(
                "UPDATE cp_tenant_accounts SET metadata = metadata - 'grandfather_overrides' "
                "WHERE id = :tid"
            ),
            {"tid": row.id},
        )


def downgrade() -> None:
    # R93[m4]: cp02's upgrade CONSUMED cp01's grandfather metadata (converted
    # to override rows, then deleted from tenant metadata). Dropping the
    # overrides table without restoring the metadata made downgrade+re-upgrade
    # silently destroy every grandfathered entitlement (tenants over community
    # defaults suddenly hard-capped). Reverse the handoff: write the override
    # rows back into metadata['grandfather_overrides'] first.
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            "SELECT tenant_id, key, value FROM cp_entitlement_overrides "
            "WHERE reason = 'migration grandfathering'"
        )
    ).fetchall()
    from collections import defaultdict

    by_tenant: dict = defaultdict(dict)
    for row in rows:
        val = row.value.get("v") if isinstance(row.value, dict) else row.value
        by_tenant[row.tenant_id][row.key] = val
    import json as _json

    for tid, overrides in by_tenant.items():
        bind.execute(
            sa.text(
                "UPDATE cp_tenant_accounts SET metadata = "
                "coalesce(metadata, '{}'::jsonb) || "
                "jsonb_build_object('grandfather_overrides', CAST(:ov AS jsonb)) "
                "WHERE id = :tid"
            ),
            {"tid": tid, "ov": _json.dumps(overrides)},
        )
    op.drop_table("cp_entitlement_overrides")
    op.drop_table("cp_plan_prices")
    op.drop_table("cp_plan_versions")
    op.drop_table("cp_product_plans")
