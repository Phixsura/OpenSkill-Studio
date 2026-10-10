"""Mapping profiles + sync engine state + generic staging (ADR-018 §10/§11, P5)

Revision ID: intg05a00005
Revises: intg04a00004
Create Date: 2026-10-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "intg05a00005"
down_revision = "intg04a00004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intg_mapping_profiles",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "connection_id",
            sa.String(26),
            sa.ForeignKey("intg_connections.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("document", JSONB, nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_mapping_org_name", "intg_mapping_profiles", ["org_id", "name"], unique=True
    )

    op.create_table(
        "intg_sync_profiles",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "connection_id",
            sa.String(26),
            sa.ForeignKey("intg_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("direction", sa.String(15), nullable=False),
        sa.Column(
            "mapping_profile_id",
            sa.String(26),
            sa.ForeignKey("intg_mapping_profiles.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("mapping_version", sa.Integer, nullable=True),
        sa.Column("schedule", sa.String(50), nullable=False),
        sa.Column("field_policy", JSONB, nullable=False, server_default="{}"),
        sa.Column("options", JSONB, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_syncprof",
        "intg_sync_profiles",
        ["connection_id", "model", "direction"],
        unique=True,
    )
    op.create_index("ix_intg_syncprof_org", "intg_sync_profiles", ["org_id", "enabled"])

    op.create_table(
        "intg_sync_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "profile_id",
            sa.String(26),
            sa.ForeignKey("intg_sync_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("trigger", sa.String(20), nullable=False),
        sa.Column("cursor_in", JSONB, nullable=False, server_default="{}"),
        sa.Column("cursor_out", JSONB, nullable=False, server_default="{}"),
        sa.Column("stats", JSONB, nullable=False, server_default="{}"),
        sa.Column("error", JSONB, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_runs_profile", "intg_sync_runs", ["profile_id", "started_at"])
    op.create_index(
        "uq_intg_run_live",
        "intg_sync_runs",
        ["profile_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued','running')"),
    )

    op.create_table(
        "intg_sync_record_results",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(26),
            sa.ForeignKey("intg_sync_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("conflict_class", sa.String(40), nullable=True),
        sa.Column("detail", JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "resolved_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("resolved_action", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intg_recres_run", "intg_sync_record_results", ["run_id", "outcome"])

    op.create_table(
        "intg_staged_records",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "connection_id",
            sa.String(26),
            sa.ForeignKey("intg_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("payload", JSONB, nullable=False, server_default="{}"),
        sa.Column("raw_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("first_seen_run_id", sa.String(26), nullable=True),
        sa.Column("last_seen_run_id", sa.String(26), nullable=True),
        sa.Column("last_outbound", JSONB, nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_intg_staged",
        "intg_staged_records",
        ["connection_id", "model", "external_id"],
        unique=True,
    )
    op.create_index(
        "ix_intg_staged_conn_model",
        "intg_staged_records",
        ["connection_id", "model", "status"],
    )


def downgrade() -> None:
    for idx, table in [
        ("ix_intg_staged_conn_model", "intg_staged_records"),
        ("uq_intg_staged", "intg_staged_records"),
    ]:
        op.drop_index(idx, table_name=table)
    op.drop_table("intg_staged_records")
    op.drop_index("ix_intg_recres_run", table_name="intg_sync_record_results")
    op.drop_table("intg_sync_record_results")
    op.drop_index("uq_intg_run_live", table_name="intg_sync_runs")
    op.drop_index("ix_intg_runs_profile", table_name="intg_sync_runs")
    op.drop_table("intg_sync_runs")
    op.drop_index("ix_intg_syncprof_org", table_name="intg_sync_profiles")
    op.drop_index("uq_intg_syncprof", table_name="intg_sync_profiles")
    op.drop_table("intg_sync_profiles")
    op.drop_index("uq_intg_mapping_org_name", table_name="intg_mapping_profiles")
    op.drop_table("intg_mapping_profiles")
