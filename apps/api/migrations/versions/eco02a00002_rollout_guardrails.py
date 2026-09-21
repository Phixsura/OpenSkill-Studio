"""eco02: rollout guardrails (ADR-016 §11.4 — LaunchDarkly lesson).

Adds eco_rollout_plans.guardrails JSONB:
  {"min_samples": int>=0, "thresholds": {"<dimension>": max_regression_float}}
Opt-in per plan; enforced by RolloutService at evaluate/promote time.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "eco02a00002"
down_revision: str = "eco01a00001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "eco_rollout_plans",
        sa.Column(
            "guardrails",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("eco_rollout_plans", "guardrails")
