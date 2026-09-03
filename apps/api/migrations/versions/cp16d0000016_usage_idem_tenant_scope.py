"""Control plane: scope usage-event idempotency to (tenant, key) + drift converge

R113[M17]: uq_cp_usage_idem (cp03c0000003) was unique on idempotency_key
alone — a global namespace, the exact cross-tenant collision cp11 (credits)
and cp13 (purchases) already fixed. The same client-supplied key on two
tenants made emit_usage's ON CONFLICT DO NOTHING match the FIRST tenant's
event and silently drop the second tenant's billable usage (sequential), or
trip the unique index (concurrent → 500). Idempotency keys are per-tenant,
so the uniqueness must be too.

R113[M16]: d5e6f70b1120 gained its certificates unique-index swap via
IN-PLACE edit (commit ea30570) after DBs had already applied the original
revision — those DBs report head yet still carry the non-unique
ix_certificates_user_path and lack uq_certificates_user_path. Recreate
defensively (IF EXISTS / IF NOT EXISTS) so drifted and fresh DBs converge.

R113[L11]: same in-place-edit drift for 10fbb2faf2d0 (commit 34e2093) —
learning_path_items skill_id/project_id FKs were edited SET NULL → CASCADE
after application. Drop + re-add with CASCADE so pre-edit DBs converge; a
no-op rewrite on fresh DBs.

Revision ID: cp16d0000016
Revises: cp15c0000015
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cp16d0000016"
down_revision: str | None = "cp15c0000015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # R113[M17]: tenant-scoped usage idempotency (template: cp11e0000011)
    op.drop_index("uq_cp_usage_idem", table_name="cp_usage_events")
    op.create_index(
        "uq_cp_usage_idem_tenant",
        "cp_usage_events",
        ["tenant_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    # R113[M16]: converge the certificates unique index — drifted DBs (applied
    # d5e6f70b1120 pre-edit) still have the non-unique index and no unique
    # one; fresh DBs already match and both statements no-op.
    op.execute("DROP INDEX IF EXISTS ix_certificates_user_path")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_certificates_user_path "
        "ON certificates (user_id, path_id)"
    )

    # R113[L11]: converge learning_path_items FK delete rules to CASCADE —
    # pre-edit DBs carry SET NULL, which orphans a NULL-ref item that then
    # violates ck_path_item_type_ref on the next row rewrite.
    for col, ref_table in (("skill_id", "skills"), ("project_id", "projects")):
        op.execute(
            f"ALTER TABLE learning_path_items "
            f"DROP CONSTRAINT IF EXISTS learning_path_items_{col}_fkey"
        )
        op.execute(
            f"ALTER TABLE learning_path_items "
            f"ADD CONSTRAINT learning_path_items_{col}_fkey "
            f"FOREIGN KEY ({col}) REFERENCES {ref_table} (id) ON DELETE CASCADE"
        )


def downgrade() -> None:
    # M16/M17-cert and L11 converge statements are intentionally NOT reverted:
    # the state they produce is exactly what the (edited) earlier migrations
    # now create, and those migrations' own downgrades remove it further down
    # the chain.
    op.drop_index("uq_cp_usage_idem_tenant", table_name="cp_usage_events")
    op.create_index(
        "uq_cp_usage_idem",
        "cp_usage_events",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
