"""Functional index on lower(users.email) (ADR-018, R334)

Revision ID: intg16a00016
Revises: intg15a00015
Create Date: 2026-10-13

The fabric's identity paths all compare `lower(users.email)` — SCIM
create/filter dup-checks, JIT verified-email matching, bulk-import row
dedup. The only email index is the plain unique btree(email), so every one
of those lookups is a sequential scan: at the 1M-row dev directory the
scale smoke measured a 500-row import commit at 87s (~175ms/row, two seq
scans each) and SCIM creates degrading the same way. This functional index
turns them all into point lookups; no semantics change (writers keep
storing emails as given, readers keep folding).
"""

import sqlalchemy as sa
from alembic import op

revision = "intg16a00016"
down_revision = "intg15a00015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_users_email_lower",
        "users",
        [sa.text("lower(email)")],
    )


def downgrade() -> None:
    op.drop_index("ix_users_email_lower", table_name="users")
