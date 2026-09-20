"""Talent layer — capability ontology, evidence ledger, passport, assessments,
credentials, employers, opportunities, applications, placements, internship
supervision, employer verification, outcome events, talent pools, outreach
(Issue #32, ADR-015)

Revision ID: talent01a00001
Revises: cp23c0000023
Create Date: 2026-09-13 16:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "talent01a00001"
down_revision: str | None = "cp23c0000023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── 1. capabilities ──
    op.create_table(
        "capabilities",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("canonical_name", sa.String(120), nullable=False, unique=True),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column(
            "parent_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "merged_into_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "capability_tag_id",
            sa.String(26),
            sa.ForeignKey("capability_tags.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("level_definitions", JSONB(), nullable=True),
        sa.Column("decay_config", JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_capabilities_category", "capabilities", ["category"])
    op.create_index("ix_capabilities_parent", "capabilities", ["parent_id"])
    op.create_index("ix_capabilities_status", "capabilities", ["status"])

    # ── 2. capability_edges ──
    op.create_table(
        "capability_edges",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "source_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("edge_type", sa.String(30), nullable=False),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("source_id != target_id", name="ck_capability_no_self_loop"),
    )
    op.create_index(
        "uq_capability_edge",
        "capability_edges",
        ["source_id", "target_id", "edge_type"],
        unique=True,
    )
    op.create_index("ix_capability_edges_target", "capability_edges", ["target_id"])

    # ── 3. capability_mappings ──
    op.create_table(
        "capability_mappings",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "capability_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_id", sa.String(26), nullable=False),
        sa.Column(
            "contribution_weight",
            sa.Numeric(3, 2),
            nullable=False,
            server_default="1.00",
        ),
        sa.Column(
            "evidence_type",
            sa.String(30),
            nullable=False,
            server_default="primary_instruction",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "contribution_weight >= 0 AND contribution_weight <= 1",
            name="ck_contribution_weight_range",
        ),
    )
    op.create_index(
        "uq_cap_mapping",
        "capability_mappings",
        ["capability_id", "source_type", "source_id"],
        unique=True,
    )
    op.create_index(
        "ix_cap_mapping_source",
        "capability_mappings",
        ["source_type", "source_id"],
    )

    # ── 4. capability_evidence ──
    op.create_table(
        "capability_evidence",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "capability_id",
            sa.String(26),
            sa.ForeignKey("capabilities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("source_id", sa.String(26), nullable=False),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("score_normalized", sa.Numeric(5, 4), nullable=True),
        sa.Column(
            "confidence",
            sa.Numeric(5, 4),
            nullable=False,
            server_default="1.0000",
        ),
        sa.Column("verification_level", sa.String(30), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supersedes_id", sa.String(26), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "score_normalized IS NULL OR (score_normalized >= 0 AND score_normalized <= 1)",
            name="ck_evidence_score_range",
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_evidence_confidence_range",
        ),
    )
    op.create_index(
        "ix_cap_evidence_user_cap",
        "capability_evidence",
        ["user_id", "capability_id", "status"],
    )
    op.create_index(
        "ix_cap_evidence_source",
        "capability_evidence",
        ["source_type", "source_id"],
    )
    op.create_index(
        "ix_cap_evidence_org",
        "capability_evidence",
        ["org_id", "capability_id"],
    )
    op.create_index(
        "ix_cap_evidence_occurred",
        "capability_evidence",
        ["user_id", "occurred_at"],
    )
    # Partial unique index: one active evidence per (user, cap, source_type, source_id)
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_cap_evidence_idempotent
            ON capability_evidence (user_id, capability_id, source_type, source_id)
            WHERE status = 'active'
            """
        )
    )

    # ── 5. skill_passports ──
    op.create_table(
        "skill_passports",
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "default_visibility",
            sa.String(20),
            nullable=False,
            server_default="private",
        ),
        sa.Column("visible_fields", JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "preferred_opportunity_types",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("availability_status", sa.String(20), nullable=True),
        sa.Column("availability_note", sa.String(500), nullable=True),
        sa.Column(
            "discoverable",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("discoverable_to", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ── 6. passport_snapshots ──
    op.create_table(
        "passport_snapshots",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("share_token", sa.String(64), nullable=False, unique=True),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("included_fields", JSONB(), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )
    op.create_index(
        "ix_passport_snapshots_user",
        "passport_snapshots",
        ["user_id", "status"],
    )

    # ── 7. assessment_blueprints ──
    op.create_table(
        "assessment_blueprints",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assessment_type", sa.String(30), nullable=False),
        sa.Column(
            "capability_requirements",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("config", JSONB(), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_assessment_blueprints_org",
        "assessment_blueprints",
        ["org_id", "status"],
    )

    # ── 8. assessment_runs ──
    op.create_table(
        "assessment_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "blueprint_id",
            sa.String(26),
            sa.ForeignKey("assessment_blueprints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("blueprint_version", sa.Integer(), nullable=False),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("results", JSONB(), nullable=True),
        sa.Column("project_id", sa.String(26), nullable=True),
        sa.Column(
            "reviewed_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_assessment_runs_user",
        "assessment_runs",
        ["user_id", "blueprint_id"],
    )
    op.create_index(
        "ix_assessment_runs_org",
        "assessment_runs",
        ["org_id", "status"],
    )

    # ── 9. credential_rules ──
    op.create_table(
        "credential_rules",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("credential_type", sa.String(80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", JSONB(), nullable=False),
        sa.Column("conditions", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "uq_credential_rule_version",
        "credential_rules",
        ["credential_type", "version"],
        unique=True,
    )

    # ── 10. credentials ──
    op.create_table(
        "credentials",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("credential_type", sa.String(80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "credential_rule_id",
            sa.String(26),
            sa.ForeignKey("credential_rules.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "issuer_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("capabilities", JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "evidence_references",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revalidation_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_credentials_user", "credentials", ["user_id", "status"])
    op.create_index(
        "ix_credentials_type",
        "credentials",
        ["credential_type", "version"],
    )
    # Partial unique: one active credential per (user, type)
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_credential_active
            ON credentials (user_id, credential_type)
            WHERE status = 'active'
            """
        )
    )

    # ── 11. employer_profiles ──
    op.create_table(
        "employer_profiles",
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("company_size", sa.String(30), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("website_url", sa.String(500), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "verification_status",
            sa.String(20),
            nullable=False,
            server_default="unverified",
        ),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ── 12. opportunities ──
    op.create_table(
        "opportunities",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "employer_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("opportunity_type", sa.String(30), nullable=False),
        sa.Column("location_mode", sa.String(20), nullable=True),
        sa.Column("location_text", sa.String(200), nullable=True),
        sa.Column("compensation_display", sa.String(200), nullable=True),
        sa.Column(
            "required_capabilities",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "preferred_capabilities",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("minimum_verification", sa.String(30), nullable=True),
        sa.Column("portfolio_requirements", sa.Text(), nullable=True),
        sa.Column("application_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("openings", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_opportunities_employer",
        "opportunities",
        ["employer_org_id", "status"],
    )
    op.create_index(
        "ix_opportunities_type",
        "opportunities",
        ["opportunity_type", "status"],
    )
    op.create_index(
        "ix_opportunities_deadline",
        "opportunities",
        ["application_deadline"],
    )

    # ── 13. applications ──
    op.create_table(
        "applications",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "opportunity_id",
            sa.String(26),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("evidence_bundle", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "passport_snapshot_id",
            sa.String(26),
            sa.ForeignKey("passport_snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("match_run_id", sa.String(26), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("resume_asset_id", sa.String(26), nullable=True),
        sa.Column("cover_note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "uq_application",
        "applications",
        ["user_id", "opportunity_id"],
        unique=True,
    )
    op.create_index(
        "ix_applications_opportunity",
        "applications",
        ["opportunity_id", "status"],
    )
    op.create_index(
        "ix_applications_user",
        "applications",
        ["user_id", "status"],
    )

    # ── 14. application_events ──
    op.create_table(
        "application_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "application_id",
            sa.String(26),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_status", sa.String(20), nullable=False),
        sa.Column("to_status", sa.String(20), nullable=False),
        # NOT nullable — structural enforcement of human-in-the-loop
        sa.Column(
            "acted_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_app_events_application",
        "application_events",
        ["application_id", "created_at"],
    )

    # ── 15. interview_stages ──
    op.create_table(
        "interview_stages",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "application_id",
            sa.String(26),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("stage_type", sa.String(30), nullable=False),
        sa.Column(
            "interviewer_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluation_notes", JSONB(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_interview_stages_app",
        "interview_stages",
        ["application_id"],
    )

    # ── 16. placements ──
    op.create_table(
        "placements",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "application_id",
            sa.String(26),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "opportunity_id",
            sa.String(26),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "employer_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role_title", sa.String(200), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("compensation_band", sa.String(100), nullable=True),
        sa.Column("placement_source", sa.String(30), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_placements_user", "placements", ["user_id"])
    op.create_index(
        "ix_placements_employer",
        "placements",
        ["employer_org_id", "status"],
    )

    # ── 17. cohort_opportunity_exposures ──
    op.create_table(
        "cohort_opportunity_exposures",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "cohort_id",
            sa.String(26),
            sa.ForeignKey("cohorts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "opportunity_id",
            sa.String(26),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exposed_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "uq_cohort_exposure",
        "cohort_opportunity_exposures",
        ["cohort_id", "opportunity_id"],
        unique=True,
    )

    # ── 18. internship_supervisions ──
    op.create_table(
        "internship_supervisions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "placement_id",
            sa.String(26),
            sa.ForeignKey("placements.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "school_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "supervisor_user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("employer_mentor_name", sa.String(100), nullable=True),
        sa.Column("milestones", JSONB(), nullable=False, server_default="[]"),
        sa.Column("notes", JSONB(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_supervisions_school",
        "internship_supervisions",
        ["school_org_id", "status"],
    )

    # ── 19. employer_verifications ──
    op.create_table(
        "employer_verifications",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "placement_id",
            sa.String(26),
            sa.ForeignKey("placements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "employer_org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "verified_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "capability_ratings",
            JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("overall_rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("overall_comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_employer_verifications_placement",
        "employer_verifications",
        ["placement_id"],
    )
    op.create_index(
        "ix_employer_verifications_user",
        "employer_verifications",
        ["user_id"],
    )

    # ── 20. outcome_events ──
    op.create_table(
        "outcome_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=True),
        sa.Column("source_id", sa.String(26), nullable=True),
        sa.Column(
            "visibility",
            sa.String(20),
            nullable=False,
            server_default="private",
        ),
        sa.Column("metadata", JSONB(), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_outcome_events_user",
        "outcome_events",
        ["user_id", "event_type"],
    )

    # ── 21. talent_pools ──
    op.create_table(
        "talent_pools",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "membership_mode",
            sa.String(20),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("rule_config", JSONB(), nullable=True),
        sa.Column(
            "visibility",
            sa.String(20),
            nullable=False,
            server_default="internal",
        ),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_talent_pools_org", "talent_pools", ["org_id"])

    # ── 22. talent_pool_memberships ──
    op.create_table(
        "talent_pool_memberships",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "pool_id",
            sa.String(26),
            sa.ForeignKey("talent_pools.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column(
            "consent_status",
            sa.String(20),
            nullable=False,
            server_default="accepted",
        ),
        sa.Column(
            "added_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "uq_pool_member",
        "talent_pool_memberships",
        ["pool_id", "user_id"],
        unique=True,
    )
    op.create_index(
        "ix_pool_memberships_user",
        "talent_pool_memberships",
        ["user_id"],
    )

    # ── 23. talent_outreach ──
    op.create_table(
        "talent_outreach",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("outreach_type", sa.String(30), nullable=False),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="sent"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_outreach_user",
        "talent_outreach",
        ["user_id", "status"],
    )
    op.create_index("ix_outreach_org", "talent_outreach", ["org_id"])


# NOTE: downgrade drops tables — run in order
def downgrade() -> None:
    # Drop in reverse FK-dependency order
    op.drop_table("talent_outreach")
    op.drop_table("talent_pool_memberships")
    op.drop_table("talent_pools")
    op.drop_table("outcome_events")
    op.drop_table("employer_verifications")
    op.drop_table("internship_supervisions")
    op.drop_table("cohort_opportunity_exposures")
    op.drop_table("placements")
    op.drop_table("interview_stages")
    op.drop_table("application_events")
    op.drop_table("applications")
    op.drop_table("opportunities")
    op.drop_table("employer_profiles")
    op.drop_table("credentials")
    op.drop_table("credential_rules")
    op.drop_table("assessment_runs")
    op.drop_table("assessment_blueprints")
    op.drop_table("passport_snapshots")
    op.drop_table("skill_passports")
    op.drop_table("capability_evidence")
    op.drop_table("capability_mappings")
    op.drop_table("capability_edges")
    op.drop_table("capabilities")
