"""Control plane: subscriptions, billing periods, invoices, payments,
webhook events (Issue #27, ADR-014 §6).

Revision ID: cp06f0000006
Revises: cp05e0000005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "cp06f0000006"
down_revision: str | None = "cp05e0000005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cp_subscriptions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column(
            "plan_version_id",
            sa.String(26),
            sa.ForeignKey("cp_plan_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("interval", sa.String(10), nullable=False),
        sa.Column("seat_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("external_customer_ref", sa.String(100), nullable=True),
        sa.Column("external_ref", sa.String(100), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_sub_live",
        "cp_subscriptions",
        ["tenant_id"],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'"),
    )
    op.create_index("ix_cp_subs_tenant", "cp_subscriptions", ["tenant_id"])
    op.create_index("ix_cp_subs_period_end", "cp_subscriptions", ["status", "current_period_end"])
    op.create_table(
        "cp_subscription_changes",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "subscription_id",
            sa.String(26),
            sa.ForeignKey("cp_subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("change_type", sa.String(20), nullable=False),
        sa.Column("from_plan_version_id", sa.String(26), nullable=True),
        sa.Column("to_plan_version_id", sa.String(26), nullable=True),
        sa.Column("from_seats", sa.Integer(), nullable=True),
        sa.Column("to_seats", sa.Integer(), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("proration_mode", sa.String(12), nullable=False, server_default="immediate"),
        sa.Column("invoiced", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_cp_sub_changes", "cp_subscription_changes", ["subscription_id", "effective_at"]
    )
    op.create_table(
        "cp_billing_periods",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column(
            "subscription_id",
            sa.String(26),
            sa.ForeignKey("cp_subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="open"),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_cp_period", "cp_billing_periods", ["subscription_id", "period_start"], unique=True
    )
    op.create_index("ix_cp_periods_status", "cp_billing_periods", ["status", "period_end"])
    op.create_table(
        "cp_invoices",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("number", sa.String(30), nullable=True, unique=True),
        sa.Column("billing_period_id", sa.String(26), nullable=True),
        sa.Column("status", sa.String(15), nullable=False, server_default="draft"),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("subtotal_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("credit_applied_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("tax_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("amount_due_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("external_ref", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("void_reason", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cp_invoices_tenant_status", "cp_invoices", ["tenant_id", "status"])
    op.create_index("ix_cp_invoices_due", "cp_invoices", ["status", "due_at"])
    op.create_table(
        "cp_invoice_lines",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "invoice_id",
            sa.String(26),
            sa.ForeignKey("cp_invoices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("line_type", sa.String(15), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 6), nullable=False, server_default="1"),
        sa.Column("unit_amount_minor", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("usage_summary", JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_cp_invoice_lines", "cp_invoice_lines", ["invoice_id", "sort_order"])
    op.create_table(
        "cp_credit_notes",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "invoice_id",
            sa.String(26),
            sa.ForeignKey("cp_invoices.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="issued"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "cp_payment_records",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "invoice_id",
            sa.String(26),
            sa.ForeignKey("cp_invoices.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("tenant_id", sa.String(26), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("method", sa.String(30), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="pending"),
        sa.Column("external_ref", sa.String(120), nullable=True),
        sa.Column("reference_note", sa.String(500), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recorded_by", sa.String(26), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_payment_external",
        "cp_payment_records",
        ["external_ref", "method"],
        unique=True,
        postgresql_where=sa.text("external_ref IS NOT NULL"),
    )
    op.create_index("ix_cp_payments_tenant", "cp_payment_records", ["tenant_id"])
    op.create_index("ix_cp_payments_invoice", "cp_payment_records", ["invoice_id"])
    op.create_table(
        "cp_invoice_sequences",
        sa.Column("scope", sa.String(10), primary_key=True),
        sa.Column("last_value", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.create_table(
        "cp_billing_webhook_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("external_event_id", sa.String(120), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(12), nullable=False, server_default="received"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "uq_cp_webhook_event",
        "cp_billing_webhook_events",
        ["provider", "external_event_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("cp_billing_webhook_events")
    op.drop_table("cp_invoice_sequences")
    op.drop_table("cp_payment_records")
    op.drop_table("cp_credit_notes")
    op.drop_table("cp_invoice_lines")
    op.drop_table("cp_invoices")
    op.drop_table("cp_billing_periods")
    op.drop_table("cp_subscription_changes")
    op.drop_table("cp_subscriptions")
