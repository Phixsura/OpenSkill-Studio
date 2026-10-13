"""R406: partial index for the connection health sweep. The sweep slices
status active/degraded ORDER BY updated_at; without this it seq-scans once
intg_connections passes ~10k rows (EXPLAIN drill, R393 class).

Revision ID: intg21a00021
Revises: intg20a00020
Create Date: 2026-10-13
"""

from alembic import op

revision = "intg21a00021"
down_revision = "intg20a00020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_intg_conn_sweep",
        "intg_connections",
        ["updated_at"],
        postgresql_where="status IN ('active','degraded')",
    )


def downgrade() -> None:
    op.drop_index("ix_intg_conn_sweep", table_name="intg_connections")
