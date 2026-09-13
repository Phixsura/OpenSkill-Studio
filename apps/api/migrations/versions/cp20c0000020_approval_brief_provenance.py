"""cp_client_approvals.completed_brief — acceptance→brief provenance.

R134 ([F1]): void-final rewinds the linked brief COMPLETED→REVIEW, but the
brief may have reached COMPLETED via update_brief BEFORE the acceptance (the
org completed it deliberately) — the guarded WHERE status==COMPLETED cannot
distinguish, so the void un-completed briefs the acceptance never touched.
Record at accept time whether THIS acceptance performed the transition; the
void rewinds only when it did.

Revision ID: cp20c0000020
Revises: cp19b0000019
"""

import sqlalchemy as sa
from alembic import op

revision = "cp20c0000020"
down_revision = "cp19b0000019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cp_client_approvals",
        sa.Column("completed_brief", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("cp_client_approvals", "completed_brief")
