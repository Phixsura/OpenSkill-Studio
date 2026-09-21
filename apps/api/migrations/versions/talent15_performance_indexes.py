"""talent15: performance indexes for scoring, matching, and webhook delivery.

Adds composite and single-column indexes on the hottest query paths:
- capability_edges(edge_type) — filtered in matching and scoring
- talent_webhook_delivery_log(status) — retry queries for pending deliveries
- opportunities(status, created_at) — open-listing sort query
"""

from alembic import op

revision: str = "talent15a00015"
down_revision: str = "talent14a00014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_capability_edges_edge_type",
        "capability_edges",
        ["edge_type"],
    )
    op.create_index(
        "ix_webhook_delivery_status",
        "talent_webhook_delivery_log",
        ["status"],
    )
    op.create_index(
        "ix_opportunities_status_created",
        "opportunities",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_opportunities_status_created", table_name="opportunities")
    op.drop_index("ix_webhook_delivery_status", table_name="talent_webhook_delivery_log")
    op.drop_index("ix_capability_edges_edge_type", table_name="capability_edges")
