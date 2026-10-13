"""R369: fabric timestamp columns NOT NULL — the models always promised
non-null (Mapped[datetime], server_default=now()) but the hand-written DDL
never said nullable=False, so the DB silently accepted NULLs the ORM can
never produce but a raw write could. Found by the fabric-scoped
model/migration parity guard (test_integrations_wiring_db).

Revision ID: intg18a00018
Revises: intg17a00017
Create Date: 2026-10-13
"""

import sqlalchemy as sa
from alembic import op

revision = "intg18a00018"
down_revision = "intg17a00017"
branch_labels = None
depends_on = None

# (table, column) — every fabric timestamp the model declares NOT NULL.
# All carry server_default=now(), so backfill is a no-op guard.
_COLS = [
    ("intg_connection_credentials", "rotated_at"),
    ("intg_connection_credentials", "created_at"),
    ("intg_connections", "created_at"),
    ("intg_connections", "updated_at"),
    ("intg_delivery_attempts", "attempted_at"),
    ("intg_event_deliveries", "created_at"),
    ("intg_event_deliveries", "updated_at"),
    ("intg_events", "time"),
    ("intg_export_runs", "created_at"),
    ("intg_export_streams", "created_at"),
    ("intg_export_streams", "updated_at"),
    ("intg_identity_links", "created_at"),
    ("intg_identity_match_queue", "created_at"),
    ("intg_import_jobs", "created_at"),
    ("intg_import_jobs", "updated_at"),
    ("intg_import_row_errors", "created_at"),
    ("intg_lti_deployments", "created_at"),
    ("intg_lti_launch_states", "created_at"),
    ("intg_lti_registrations", "created_at"),
    ("intg_lti_registrations", "updated_at"),
    ("intg_lti_resource_links", "created_at"),
    ("intg_lti_tool_keys", "created_at"),
    ("intg_mapping_profiles", "created_at"),
    ("intg_mapping_profiles", "updated_at"),
    ("intg_org_domains", "created_at"),
    ("intg_providers", "created_at"),
    ("intg_providers", "updated_at"),
    ("intg_scim_group_members", "created_at"),
    ("intg_scim_groups", "created_at"),
    ("intg_scim_groups", "updated_at"),
    ("intg_scim_tokens", "created_at"),
    ("intg_sso_connections", "created_at"),
    ("intg_sso_connections", "updated_at"),
    ("intg_sso_login_states", "created_at"),
    ("intg_staged_records", "updated_at"),
    ("intg_staged_records", "created_at"),
    ("intg_sync_profiles", "created_at"),
    ("intg_sync_profiles", "updated_at"),
    ("intg_sync_record_results", "created_at"),
    ("intg_sync_runs", "created_at"),
]


def upgrade() -> None:
    for table, col in _COLS:
        # Defensive backfill: server_default means NULLs cannot normally
        # exist, but SET NOT NULL must never fail on a dirty row.
        op.execute(f'UPDATE {table} SET "{col}" = now() WHERE "{col}" IS NULL')
        op.alter_column(table, col, existing_type=sa.DateTime(timezone=True), nullable=False)


def downgrade() -> None:
    for table, col in reversed(_COLS):
        op.alter_column(table, col, existing_type=sa.DateTime(timezone=True), nullable=True)
