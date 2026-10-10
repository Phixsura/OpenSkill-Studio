"""assignment (experiment_id, assigned_at) index for windowed SRM (ADR-017 §9, round 633)

Defect #90 added a windowed SRM check that filters assignments by
experiment_id + assigned_at on every guardrail sweep. The exposures
table already carries the analogous (experiment_id, occurred_at) index;
this brings assignments to parity so the hot window query never
heap-filters a large experiment.

Revision ID: exp17a00017
Revises: exp16a00016
Create Date: 2026-10-07
"""

from alembic import op

revision = "exp17a00017"
down_revision = "exp16a00016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_experiment_assignments_exp_assigned",
        "experiment_assignments",
        ["experiment_id", "assigned_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_experiment_assignments_exp_assigned",
        table_name="experiment_assignments",
    )
