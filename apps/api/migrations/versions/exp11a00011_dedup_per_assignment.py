"""exp11 exposure dedup scoped per ASSIGNMENT (ADR-017 §18 round 64)

Defect #58: the dedup unique index was (experiment_id, dedup_key) — two
UNITS sharing a natural key (e.g. a per-day client key like 'todo-<date>')
collided, and ON CONFLICT DO NOTHING silently dropped every unit after the
first each day. Idempotency is per assignment, not per experiment. The new
uniqueness is strictly narrower, so existing rows always satisfy it.

Revision ID: exp11a00011
Revises: exp10a00010
Create Date: 2026-10-02

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "exp11a00011"
down_revision: str | None = "exp10a00010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "experiment_exposures"
_INDEX = "uq_experiment_exposures_dedup"


def upgrade() -> None:
    op.drop_index(_INDEX, table_name=_TABLE)
    op.create_index(
        _INDEX,
        _TABLE,
        ["assignment_id", "dedup_key"],
        unique=True,
        postgresql_where=text("dedup_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(_INDEX, table_name=_TABLE)
    op.create_index(
        _INDEX,
        _TABLE,
        ["experiment_id", "dedup_key"],
        unique=True,
        postgresql_where=text("dedup_key IS NOT NULL"),
    )
