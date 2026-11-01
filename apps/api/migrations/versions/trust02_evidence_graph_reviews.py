"""trust02: Evidence Graph & Human Oversight (ADR-017 Phase 2).

Creates:
- trust_assurance_cases: claims about AI system properties
- trust_evidence_items: versioned evidence with provenance & expiry
- trust_evidence_links: many-to-many case ↔ evidence with relation type
- trust_review_requests: human review queue with assignment & due dates
- trust_review_decisions: append-only decision records

Revision ID: trust02a00002
Revises: trust01a00001
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "trust02a00002"
down_revision: str = "trust01a00001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ────────────────────────────────────────────────────────
    trust_claim_status = sa.Enum(
        "draft", "active", "challenged", "retired",
        name="trust_claim_status", create_constraint=True,
    )
    trust_evidence_type = sa.Enum(
        "benchmark", "experiment", "evaluation", "red_team", "app_review",
        "privacy_assessment", "incident_report", "human_attestation",
        "external_audit", "policy_simulation", "custom",
        name="trust_evidence_type", create_constraint=True,
    )
    trust_evidence_status = sa.Enum(
        "draft", "valid", "stale", "revoked", "superseded",
        name="trust_evidence_status", create_constraint=True,
    )
    trust_link_relation = sa.Enum(
        "supports", "weakens", "mitigates", "depends_on",
        name="trust_link_relation", create_constraint=True,
    )
    trust_review_type = sa.Enum(
        "risk_assessment", "release_gate", "evidence_review",
        "exception_request", "incident_closure", "policy_change",
        name="trust_review_type", create_constraint=True,
    )
    trust_review_status = sa.Enum(
        "pending", "in_review", "approved", "rejected",
        "returned", "expired", "cancelled",
        name="trust_review_status", create_constraint=True,
    )
    trust_review_decision_type = sa.Enum(
        "approve", "reject", "return", "escalate",
        name="trust_review_decision_type", create_constraint=True,
    )

    # ── trust_assurance_cases ────────────────────────────────────────
    op.create_table(
        "trust_assurance_cases",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("claim", sa.Text, nullable=False),
        sa.Column("status", trust_claim_status, nullable=False, server_default="draft"),
        sa.Column("owner_user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_case_system", "trust_assurance_cases", ["system_id"])
    op.create_index("ix_trust_case_org_status", "trust_assurance_cases", ["org_id", "status"])

    # ── trust_evidence_items ─────────────────────────────────────────
    op.create_table(
        "trust_evidence_items",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("evidence_type", trust_evidence_type, nullable=False),
        sa.Column("status", trust_evidence_status, nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("source_type", sa.String(40), nullable=True),
        sa.Column("source_id", sa.String(26), nullable=True),
        sa.Column("source_version", sa.String(50), nullable=True),
        sa.Column("scope", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revalidation_rule", sa.String(200), nullable=True),
        sa.Column("content", postgresql.JSONB, nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("collected_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_evidence_org", "trust_evidence_items", ["org_id"])
    op.create_index("ix_trust_evidence_type_status", "trust_evidence_items", ["evidence_type", "status"])
    op.create_index("ix_trust_evidence_source", "trust_evidence_items", ["source_type", "source_id"])

    # ── trust_evidence_links ─────────────────────────────────────────
    op.create_table(
        "trust_evidence_links",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("case_id", sa.String(26), sa.ForeignKey("trust_assurance_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id", sa.String(26), sa.ForeignKey("trust_evidence_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation", trust_link_relation, nullable=False, server_default="supports"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("linked_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_trust_evidence_link", "trust_evidence_links", ["case_id", "evidence_id"], unique=True)
    op.create_index("ix_trust_link_evidence", "trust_evidence_links", ["evidence_id"])

    # ── trust_review_requests ────────────────────────────────────────
    op.create_table(
        "trust_review_requests",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("review_type", trust_review_type, nullable=False),
        sa.Column("status", trust_review_status, nullable=False, server_default="pending"),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("requested_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("assigned_to", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("context", postgresql.JSONB, nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_review_org_status", "trust_review_requests", ["org_id", "status"])
    op.create_index("ix_trust_review_target", "trust_review_requests", ["target_type", "target_id"])
    op.create_index("ix_trust_review_assignee", "trust_review_requests", ["assigned_to"])
    op.create_index("ix_trust_review_due", "trust_review_requests", ["due_at"])

    # ── trust_review_decisions ───────────────────────────────────────
    op.create_table(
        "trust_review_decisions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("request_id", sa.String(26), sa.ForeignKey("trust_review_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("decision", trust_review_decision_type, nullable=False),
        sa.Column("reviewer_id", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("rationale", sa.Text, nullable=False),
        sa.Column("conditions", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_decision_request", "trust_review_decisions", ["request_id"])
    op.create_index("ix_trust_decision_reviewer", "trust_review_decisions", ["reviewer_id"])


def downgrade() -> None:
    op.drop_table("trust_review_decisions")
    op.drop_table("trust_review_requests")
    op.drop_table("trust_evidence_links")
    op.drop_table("trust_evidence_items")
    op.drop_table("trust_assurance_cases")
    op.execute("DROP TYPE IF EXISTS trust_review_decision_type")
    op.execute("DROP TYPE IF EXISTS trust_review_status")
    op.execute("DROP TYPE IF EXISTS trust_review_type")
    op.execute("DROP TYPE IF EXISTS trust_link_relation")
    op.execute("DROP TYPE IF EXISTS trust_evidence_status")
    op.execute("DROP TYPE IF EXISTS trust_evidence_type")
    op.execute("DROP TYPE IF EXISTS trust_claim_status")
