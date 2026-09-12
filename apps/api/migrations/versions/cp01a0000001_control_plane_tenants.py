"""Control plane: tenants, members, platform roles, impersonation, audit,
outbox + organizations.tenant_id backfill (Issue #27, ADR-014 §1).

Three steps in one revision:
 1. create cp_* tables + nullable organizations.tenant_id
 2. data backfill: one DIRECT tenant per existing org (owner from org OWNER
    members, fallback created_by) + grandfathering entitlement overrides for
    tenants already above community defaults
 3. ALTER organizations.tenant_id SET NOT NULL

Downgrade drops the column and tables (destructive — backfilled tenants are
derived data at this point in history, so a downgrade loses only cp rows).

Revision ID: cp01a0000001
Revises: a1b2c3d4e5f6
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from ulid import ULID

revision: str = "cp01a0000001"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_tenant_status = sa.Enum(
    "TRIAL",
    "ACTIVE",
    "PAST_DUE",
    "SUSPENDED",
    "CANCELLED",
    "ARCHIVED",
    name="cp_tenant_status",
)
_account_type = sa.Enum(
    "DIRECT",
    "PARTNER_MANAGED",
    "OEM",
    "ENTERPRISE",
    "INTERNAL",
    name="cp_tenant_account_type",
)


def upgrade() -> None:
    # ── 1. Tables ────────────────────────────────────────────
    op.create_table(
        "cp_tenant_accounts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("status", _tenant_status, nullable=False, server_default="TRIAL"),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("account_type", _account_type, nullable=False, server_default="DIRECT"),
        sa.Column("billing_email", sa.String(255), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("attributed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspension_reason", sa.String(500), nullable=True),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
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
    op.create_index("ix_cp_tenants_status", "cp_tenant_accounts", ["status"])
    op.create_index("ix_cp_tenants_partner", "cp_tenant_accounts", ["partner_id"])

    op.create_table(
        "cp_tenant_members",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.String(26),
            sa.ForeignKey("cp_tenant_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(30), nullable=False),
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
    op.create_index(
        "uq_cp_tenant_member", "cp_tenant_members", ["tenant_id", "user_id"], unique=True
    )
    op.create_index("ix_cp_tenant_members_user", "cp_tenant_members", ["user_id"])

    op.create_table(
        "cp_platform_roles",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column(
            "granted_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("uq_cp_platform_role", "cp_platform_roles", ["user_id", "role"], unique=True)

    op.create_table(
        "cp_impersonation_grants",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "platform_user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.String(26),
            sa.ForeignKey("cp_tenant_accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_cp_imp_grants_platform_user",
        "cp_impersonation_grants",
        ["platform_user_id", "created_at"],
    )
    op.create_index("ix_cp_imp_grants_target", "cp_impersonation_grants", ["target_user_id"])

    op.create_table(
        "cp_audit_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "actor_user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("partner_id", sa.String(26), nullable=True),
        sa.Column("before", JSONB(), nullable=True),
        sa.Column("after", JSONB(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cp_audit_tenant_created", "cp_audit_events", ["tenant_id", "created_at"])
    op.create_index("ix_cp_audit_action_created", "cp_audit_events", ["action", "created_at"])
    op.create_index("ix_cp_audit_target", "cp_audit_events", ["target_type", "target_id"])

    op.create_table(
        "cp_outbox",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("topic", sa.String(40), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(12), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("locked_by", sa.String(64), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_cp_outbox_poll", "cp_outbox", ["status", "available_at"])

    # organizations.tenant_id — nullable first, backfill, then NOT NULL
    op.add_column("organizations", sa.Column("tenant_id", sa.String(26), nullable=True))
    op.create_foreign_key(
        "fk_orgs_tenant",
        "organizations",
        "cp_tenant_accounts",
        ["tenant_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_orgs_tenant", "organizations", ["tenant_id"])

    # ── 2. Backfill ──────────────────────────────────────────
    bind = op.get_bind()
    orgs = bind.execute(
        sa.text("SELECT id, name, slug, status, created_by FROM organizations ORDER BY created_at")
    ).fetchall()

    # Community defaults for grandfathering (mirror of ENTITLEMENT_DEFS)
    community = {"max_organizations": 1, "max_active_learners": 25, "max_instructors": 3}

    for org in orgs:
        tenant_id = str(ULID())
        # Org statuses map 1:1 (ACTIVE/SUSPENDED/ARCHIVED share names);
        # backfilled tenants get NO trial.
        status = {"ACTIVE": "ACTIVE", "SUSPENDED": "SUSPENDED", "ARCHIVED": "ARCHIVED"}.get(
            str(org.status), "ACTIVE"
        )
        bind.execute(
            sa.text(
                "INSERT INTO cp_tenant_accounts "
                "(id, name, slug, status, account_type, currency, timezone, metadata, created_by, created_at, updated_at) "
                "VALUES (:id, :name, :slug, :status, 'DIRECT', 'USD', 'UTC', '{}', :created_by, now(), now())"
            ),
            {
                "id": tenant_id,
                "name": org.name,
                "slug": org.slug,  # tenants table empty + org slugs unique → no collision
                "status": status,
                "created_by": org.created_by,
            },
        )
        bind.execute(
            sa.text("UPDATE organizations SET tenant_id = :tid WHERE id = :oid"),
            {"tid": tenant_id, "oid": org.id},
        )
        # Tenant owners = active org OWNER members; fallback created_by.
        owners = bind.execute(
            sa.text(
                "SELECT user_id FROM org_members "
                "WHERE org_id = :oid AND role = 'OWNER' AND status = 'ACTIVE'"
            ),
            {"oid": org.id},
        ).fetchall()
        owner_ids = [o.user_id for o in owners] or ([org.created_by] if org.created_by else [])
        for uid in dict.fromkeys(owner_ids):  # dedupe, keep order
            bind.execute(
                sa.text(
                    "INSERT INTO cp_tenant_members (id, tenant_id, user_id, role, created_at) "
                    "VALUES (:id, :tid, :uid, 'owner', now()) ON CONFLICT DO NOTHING"
                ),
                {"id": str(ULID()), "tid": tenant_id, "uid": uid},
            )

    # Grandfathering: overrides for anything already above community defaults.
    # (cp_entitlement_overrides lands in the P2 migration — record the
    # grandfather data in tenant metadata now; the P2 migration converts it
    # into real override rows.)
    grandfather_rows = bind.execute(
        sa.text(
            """
            SELECT t.id AS tenant_id,
                   COUNT(DISTINCT o.id) AS org_count,
                   COUNT(DISTINCT om.user_id) FILTER (WHERE om.role = 'STUDENT' AND om.status = 'ACTIVE') AS learners,
                   COUNT(DISTINCT om.user_id) FILTER (WHERE om.role IN ('INSTRUCTOR','ADMIN','OWNER') AND om.status = 'ACTIVE') AS instructors
            FROM cp_tenant_accounts t
            JOIN organizations o ON o.tenant_id = t.id
            LEFT JOIN org_members om ON om.org_id = o.id
            GROUP BY t.id
            """
        )
    ).fetchall()
    import json

    for row in grandfather_rows:
        overrides = {}
        if row.org_count > community["max_organizations"]:
            overrides["max_organizations"] = row.org_count
        if (row.learners or 0) > community["max_active_learners"]:
            overrides["max_active_learners"] = row.learners
        if (row.instructors or 0) > community["max_instructors"]:
            overrides["max_instructors"] = row.instructors
        if overrides:
            bind.execute(
                sa.text(
                    "UPDATE cp_tenant_accounts SET metadata = metadata || :patch WHERE id = :tid"
                ),
                {
                    "patch": json.dumps({"grandfather_overrides": overrides}),
                    "tid": row.tenant_id,
                },
            )

    # ── 3. NOT NULL ──────────────────────────────────────────
    op.alter_column("organizations", "tenant_id", nullable=False)


def downgrade() -> None:
    op.drop_index("ix_orgs_tenant", table_name="organizations")
    op.drop_constraint("fk_orgs_tenant", "organizations", type_="foreignkey")
    op.drop_column("organizations", "tenant_id")
    op.drop_table("cp_outbox")
    op.drop_table("cp_audit_events")
    op.drop_table("cp_impersonation_grants")
    op.drop_table("cp_platform_roles")
    op.drop_table("cp_tenant_members")
    op.drop_table("cp_tenant_accounts")
    _tenant_status.drop(op.get_bind(), checkfirst=True)
    _account_type.drop(op.get_bind(), checkfirst=True)
