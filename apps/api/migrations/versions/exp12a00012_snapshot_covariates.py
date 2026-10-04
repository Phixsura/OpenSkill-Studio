"""exp12 multi-covariate CUPED storage (ADR-017 §4.6 v3, round 113)

Per-covariate sufficient statistics live in a JSONB map
{cov_key: {sum, sum_sq, xy_sum}}; the existing cov_* columns stay as the
FIRST covariate's mirror so every pre-exp12 analysis path keeps working.

Revision ID: exp12a00012
Revises: exp11a00011
Create Date: 2026-10-03

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "exp12a00012"
down_revision: str | None = "exp11a00011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "experiment_metric_snapshots",
        sa.Column("covariates", JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
    )


def downgrade() -> None:
    op.drop_column("experiment_metric_snapshots", "covariates")
