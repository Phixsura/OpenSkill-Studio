"""Time index on intg_events (ADR-018, R336 — retention cutoff scan)

Revision ID: intg17a00017
Revises: intg16a00016
Create Date: 2026-10-13

The nightly retention sweep deletes events by a GLOBAL `time < cutoff` —
the only time-bearing index is (org_id, type, time), whose leading column
makes it useless for the cutoff, so the fastest-growing fabric table
(every mesh emit lands here) was sequential-scanned nightly. Found by the
R336 EXPLAIN audit over every fabric hot-path predicate.
"""

from alembic import op

revision = "intg17a00017"
down_revision = "intg16a00016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_intg_events_time", "intg_events", ["time"])


def downgrade() -> None:
    op.drop_index("ix_intg_events_time", table_name="intg_events")
