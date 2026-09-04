"""R134 [0]/[1]/[2]/[15]: invoice close snapshot.

Adds cp_invoices.close_snapshot — stamped by close_period_and_invoice under
the Subscription FOR UPDATE with the arrears basis, the rollover fold's
pre/post values, and the set of immediate changes visible at close time.
A void/re-close reads the original close's decisions from here instead of
re-deriving them from transaction timestamps (whose order does not track
sub-lock serialization) or global change-id order.

Revision ID: cp21c0000021
Revises: cp20c0000020
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "cp21c0000021"
down_revision = "cp20c0000020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cp_invoices",
        sa.Column("close_snapshot", JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cp_invoices", "close_snapshot")
