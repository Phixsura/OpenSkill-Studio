"""Control plane: settlement/void indexes + author_id FK divergence (R50).

R50[43]: cp_usage_events.workflow_run_id had no index — handle_run_terminal
(every credit-enforced run's terminal transition) full-scanned the append-only
usage table to find the run's events.

R50[44]: cp_rated_usage.invoice_line_id had no index — void_invoice's unbind
UPDATE, margin rev-share accrual, and the invoice-line trace endpoint all
filter on it and full-scanned.

R50[45]: submission_comments.author_id FK was created (c93d15e07f2a) with no
ondelete (NO ACTION) but the model declares SET NULL — deleting a user with
comments raised an FK violation instead of nulling authorship (guest comments
already carry client_author_label as the surviving record). Recreate the FK
to match the model.

Revision ID: cp14b0000014
Revises: cp13a0000013
"""

from collections.abc import Sequence

from alembic import op

revision: str = "cp14b0000014"
down_revision: str | None = "cp13a0000013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_cp_usage_workflow_run",
        "cp_usage_events",
        ["workflow_run_id"],
        postgresql_where="workflow_run_id IS NOT NULL",
    )
    op.create_index(
        "ix_cp_rated_invoice_line",
        "cp_rated_usage",
        ["invoice_line_id"],
        postgresql_where="invoice_line_id IS NOT NULL",
    )
    op.drop_constraint("submission_comments_author_id_fkey", "submission_comments")
    op.create_foreign_key(
        "submission_comments_author_id_fkey",
        "submission_comments",
        "users",
        ["author_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("submission_comments_author_id_fkey", "submission_comments")
    op.create_foreign_key(
        "submission_comments_author_id_fkey",
        "submission_comments",
        "users",
        ["author_id"],
        ["id"],
    )
    op.drop_index("ix_cp_rated_invoice_line", table_name="cp_rated_usage")
    op.drop_index("ix_cp_usage_workflow_run", table_name="cp_usage_events")
