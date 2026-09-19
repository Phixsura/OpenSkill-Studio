"""talent14: portfolio, offers, onboarding, messaging, webhooks, succession models.

Revision ID: talent14a00014
Revises: talent13a00013
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "talent14a00014"
down_revision = "talent13a00013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_portfolio_items",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("user_id", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_type", sa.String(30), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("capability_ids", postgresql.JSONB, server_default="[]"),
        sa.Column("visibility", sa.String(20), server_default="private"),
        sa.Column("pinned", sa.Boolean, server_default="false"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_portfolio_user", "talent_portfolio_items", ["user_id"])

    op.create_table(
        "talent_offers",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "application_id", sa.String(26), sa.ForeignKey("applications.id"), nullable=False
        ),
        sa.Column(
            "employer_org_id", sa.String(26), sa.ForeignKey("organizations.id"), nullable=False
        ),
        sa.Column("role_title", sa.String(200), nullable=False),
        sa.Column("compensation_text", sa.String(500), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("conditions", postgresql.JSONB, server_default="[]"),
        sa.Column("custom_sections", postgresql.JSONB, server_default="[]"),
        sa.Column("status", sa.String(20), server_default="'draft'"),
        sa.Column("negotiation_history", postgresql.JSONB, server_default="[]"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("declined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decline_reason", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_offers_app", "talent_offers", ["application_id"])
    op.create_index("ix_offers_org", "talent_offers", ["employer_org_id"])

    op.create_table(
        "talent_onboarding_templates",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tasks", postgresql.JSONB, server_default="[]"),
        sa.Column("status", sa.String(20), server_default="'active'"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_onboard_tmpl_org", "talent_onboarding_templates", ["org_id"])

    op.create_table(
        "talent_onboarding_checklists",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("placement_id", sa.String(26), sa.ForeignKey("placements.id"), nullable=False),
        sa.Column(
            "template_id",
            sa.String(26),
            sa.ForeignKey("talent_onboarding_templates.id"),
            nullable=True,
        ),
        sa.Column("tasks", postgresql.JSONB, server_default="[]"),
        sa.Column("completion_percentage", sa.SmallInteger, server_default="0"),
        sa.Column("current_phase", sa.String(30), server_default="'pre_start'"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_onboard_cl_placement", "talent_onboarding_checklists", ["placement_id"])

    op.create_table(
        "talent_application_messages",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "application_id", sa.String(26), sa.ForeignKey("applications.id"), nullable=False
        ),
        sa.Column("sender_id", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sender_role", sa.String(20), nullable=False),
        sa.Column("message_type", sa.String(30), server_default="'text'"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("attachments", postgresql.JSONB, server_default="[]"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_msg_app", "talent_application_messages", ["application_id"])
    op.create_index("ix_msg_sender", "talent_application_messages", ["sender_id"])

    op.create_table(
        "talent_webhook_endpoints",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("secret", sa.String(200), nullable=False),
        sa.Column("event_types", postgresql.JSONB, server_default="[]"),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_webhook_org", "talent_webhook_endpoints", ["org_id"])

    op.create_table(
        "talent_webhook_delivery_log",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "endpoint_id",
            sa.String(26),
            sa.ForeignKey("talent_webhook_endpoints.id"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB, server_default="{}"),
        sa.Column("status", sa.String(20), server_default="'pending'"),
        sa.Column("response_code", sa.Integer, nullable=True),
        sa.Column("attempts", sa.Integer, server_default="0"),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_wh_log_endpoint", "talent_webhook_delivery_log", ["endpoint_id"])

    op.create_table(
        "talent_key_roles",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("required_capabilities", postgresql.JSONB, server_default="[]"),
        sa.Column("current_holder_id", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("criticality", sa.String(20), server_default="'medium'"),
        sa.Column("status", sa.String(20), server_default="'active'"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_keyrole_org", "talent_key_roles", ["org_id"])

    op.create_table(
        "talent_successor_nominations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "key_role_id", sa.String(26), sa.ForeignKey("talent_key_roles.id"), nullable=False
        ),
        sa.Column("candidate_user_id", sa.String(26), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("readiness", sa.String(30), server_default="'not_assessed'"),
        sa.Column("capability_match", sa.Float, nullable=True),
        sa.Column("gaps", postgresql.JSONB, server_default="[]"),
        sa.Column("development_plan", postgresql.JSONB, server_default="[]"),
        sa.Column("nominated_by", sa.String(26), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_successor_role", "talent_successor_nominations", ["key_role_id"])
    op.create_index("ix_successor_user", "talent_successor_nominations", ["candidate_user_id"])


def downgrade() -> None:
    op.drop_table("talent_successor_nominations")
    op.drop_table("talent_key_roles")
    op.drop_table("talent_webhook_delivery_log")
    op.drop_table("talent_webhook_endpoints")
    op.drop_table("talent_application_messages")
    op.drop_table("talent_onboarding_checklists")
    op.drop_table("talent_onboarding_templates")
    op.drop_table("talent_offers")
    op.drop_table("talent_portfolio_items")
