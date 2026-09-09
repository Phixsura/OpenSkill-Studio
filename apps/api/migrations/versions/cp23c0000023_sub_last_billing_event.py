"""R167: subscription last_billing_event_at — Stripe event-ordering high-water.

Stripe delivers webhook events with NO ordering guarantee. The invoice.paid
(→active) and invoice.payment_failed (→past_due) status transitions were
applied purely by event type, so a late-delivered stale event flipped the
subscription (and tenant) to the WRONG billing state — a paying customer
wrongly past_due (features blocked), or (revenue side) past_due not enforced.
This column records the created-time of the newest billing event applied so
stale ones are ignored.

Revision ID: cp23c0000023
Revises: cp22c0000022
"""

import sqlalchemy as sa
from alembic import op

revision = "cp23c0000023"
down_revision = "cp22c0000022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cp_subscriptions",
        sa.Column("last_billing_event_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cp_subscriptions", "last_billing_event_at")
