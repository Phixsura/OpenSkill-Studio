"""Workflow packs trio + runtime + bindings + ComfyUI imports (Issue #21, ADR-010)

Revision ID: a8b92d334102
Revises: f7a81c223001
Create Date: 2026-08-23 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, JSONB

# revision identifiers, used by Alembic.
revision: str = "a8b92d334102"
down_revision: str | None = "f7a81c223001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Reuse existing PG enums from the skill-pack migrations (create_type=False)
pack_status = ENUM("DRAFT", "PUBLISHED", "ARCHIVED", name="pack_status", create_type=False)
pack_visibility = ENUM("PRIVATE", "UNLISTED", "PUBLIC", name="pack_visibility", create_type=False)
install_status = ENUM("ACTIVE", "FORKED", "REMOVED", name="install_status", create_type=False)


def upgrade() -> None:
    # Create the new enum types once, then reference with create_type=False
    ENUM(
        "PENDING", "RUNNING", "WAITING_REVIEW", "COMPLETED", "FAILED", "CANCELLED",
        name="workflow_run_status",
    ).create(op.get_bind(), checkfirst=True)
    ENUM(
        "PENDING", "READY", "RUNNING", "WAITING_REVIEW", "WAITING_RETRY",
        "COMPLETED", "FAILED", "SKIPPED", "CANCELLED",
        name="workflow_step_run_status",
    ).create(op.get_bind(), checkfirst=True)
    run_status = ENUM(
        "PENDING", "RUNNING", "WAITING_REVIEW", "COMPLETED", "FAILED", "CANCELLED",
        name="workflow_run_status", create_type=False,
    )
    step_run_status = ENUM(
        "PENDING", "READY", "RUNNING", "WAITING_REVIEW", "WAITING_RETRY",
        "COMPLETED", "FAILED", "SKIPPED", "CANCELLED",
        name="workflow_step_run_status", create_type=False,
    )

    # ── workflow_packs ──
    op.create_table(
        "workflow_packs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "owner_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("summary", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", pack_status, nullable=False, server_default="DRAFT"),
        sa.Column("visibility", pack_visibility, nullable=False, server_default="PRIVATE"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("cover_image_key", sa.String(500), nullable=True),
        sa.Column("workflow_type", sa.String(50), nullable=False, server_default="production"),
        sa.Column("scenario_tags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("tool_tags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("capability_tags", JSONB(), nullable=False, server_default="[]"),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("install_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("review_status", sa.String(20), nullable=True),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        sa.Column("provenance", JSONB(), nullable=False, server_default="{}"),
        sa.Column("definition", JSONB(), nullable=False, server_default="{}"),
        sa.Column("input_schema", JSONB(), nullable=False, server_default="[]"),
        sa.Column("output_schema", JSONB(), nullable=False, server_default="[]"),
        sa.Column("definition_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint(
            "octet_length(definition::text) <= 262144", name="ck_wfpack_definition_size"
        ),
    )
    op.create_index("uq_wfpack_org_slug", "workflow_packs", ["owner_org_id", "slug"], unique=True)
    op.create_index("ix_wfpacks_visibility_status", "workflow_packs", ["visibility", "status"])

    # ── workflow_pack_releases ──
    op.create_table(
        "workflow_pack_releases",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("workflow_packs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("manifest", JSONB(), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("step_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deprecated_by", sa.String(26), nullable=True),
        sa.Column(
            "released_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "released_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index("uq_wfrelease_version", "workflow_pack_releases", ["pack_id", "version"], unique=True)
    op.create_index("ix_wfreleases_pack_date", "workflow_pack_releases", ["pack_id", "released_at"])

    # ── workflow_pack_installations ──
    op.create_table(
        "workflow_pack_installations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pack_id",
            sa.String(26),
            sa.ForeignKey("workflow_packs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "release_id",
            sa.String(26),
            sa.ForeignKey("workflow_pack_releases.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("installed_version", sa.String(50), nullable=False),
        sa.Column("status", install_status, nullable=False, server_default="ACTIVE"),
        sa.Column("local_definition", JSONB(), nullable=True),
        sa.Column("locally_modified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "installed_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "installed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index(
        "uq_wfinstall_org_pack", "workflow_pack_installations", ["org_id", "pack_id"], unique=True
    )
    op.create_index("ix_wfinstalls_org", "workflow_pack_installations", ["org_id"])

    # ── comfyui_imports ──
    op.create_table(
        "comfyui_imports",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pack_id", sa.String(26), nullable=True),
        sa.Column("original_json", JSONB(), nullable=False),
        sa.Column("original_sha256", sa.String(64), nullable=False),
        sa.Column("format_detected", sa.String(20), nullable=False),
        sa.Column("dependency_report", JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="imported"),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index("ix_comfyui_imports_org", "comfyui_imports", ["org_id"])

    # ── workflow_runs ──
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pack_id", sa.String(26), nullable=True),
        sa.Column("release_id", sa.String(26), nullable=True),
        sa.Column(
            "installation_id",
            sa.String(26),
            sa.ForeignKey("workflow_pack_installations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("definition_snapshot", JSONB(), nullable=False),
        sa.Column("inputs", JSONB(), nullable=False, server_default="{}"),
        sa.Column("outputs", JSONB(), nullable=True),
        sa.Column("status", run_status, nullable=False, server_default="PENDING"),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column(
            "started_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_wfruns_org_status", "workflow_runs", ["org_id", "status"])
    op.create_index(
        "uq_wfrun_idem",
        "workflow_runs",
        ["org_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    # ── workflow_step_runs ──
    op.create_table(
        "workflow_step_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(26),
            sa.ForeignKey("workflow_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", sa.String(64), nullable=False),
        sa.Column("step_type", sa.String(30), nullable=False),
        sa.Column("status", step_run_status, nullable=False, server_default="PENDING"),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("inputs_resolved", JSONB(), nullable=True),
        sa.Column("output", JSONB(), nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("provider_request_id", sa.String(100), nullable=True),
        sa.Column("offering_id", sa.String(26), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index("uq_steprun", "workflow_step_runs", ["run_id", "step_id"], unique=True)
    op.create_index("ix_stepruns_status", "workflow_step_runs", ["status", "lease_expires_at"])

    # ── workflow_step_reviews ──
    op.create_table(
        "workflow_step_reviews",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "step_run_id",
            sa.String(26),
            sa.ForeignKey("workflow_step_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decision", sa.String(20), nullable=True),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column(
            "decided_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index(
        "uq_open_review",
        "workflow_step_reviews",
        ["step_run_id"],
        unique=True,
        postgresql_where=sa.text("decision IS NULL"),
    )
    op.create_index("ix_step_reviews_org_due", "workflow_step_reviews", ["org_id", "due_at"])

    # ── workflow_run_events ──
    op.create_table(
        "workflow_run_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(26),
            sa.ForeignKey("workflow_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", sa.String(64), nullable=True),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index("ix_runevents_run", "workflow_run_events", ["run_id", "created_at"])

    # ── workflow_step_bindings ──
    op.create_table(
        "workflow_step_bindings",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "installation_id",
            sa.String(26),
            sa.ForeignKey("workflow_pack_installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", sa.String(64), nullable=False),
        sa.Column("binding_mode", sa.String(20), nullable=False, server_default="auto"),
        sa.Column(
            "offering_id",
            sa.String(26),
            sa.ForeignKey("provider_model_offerings.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reasons", JSONB(), nullable=False, server_default="[]"),
        sa.Column("gaps", JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "confirmed_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.create_index("uq_binding", "workflow_step_bindings", ["installation_id", "step_id"], unique=True)


def downgrade() -> None:
    op.drop_table("workflow_step_bindings")
    op.drop_table("workflow_run_events")
    op.drop_table("workflow_step_reviews")
    op.drop_table("workflow_step_runs")
    op.drop_table("workflow_runs")
    op.drop_table("comfyui_imports")
    op.drop_table("workflow_pack_installations")
    op.drop_table("workflow_pack_releases")
    op.drop_table("workflow_packs")
    sa.Enum(name="workflow_step_run_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="workflow_run_status").drop(op.get_bind(), checkfirst=True)
