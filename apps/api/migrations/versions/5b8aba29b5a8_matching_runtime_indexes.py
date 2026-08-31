"""Add org-scoped list indexes + match_results (run, entity) uniqueness

Revision ID: 5b8aba29b5a8
Revises: c1db4f556304
Create Date: 2026-08-25 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b8aba29b5a8"
down_revision: str | None = "c1db4f556304"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Org-scoped assignment lists filtered only through the (project_id,
    # user_id) unique index before — org-wide views were sequential scans.
    op.create_index("ix_creator_assignments_org", "creator_assignments", ["org_id"])
    # Run history lists sort by created_at; ix_wfruns_org_status only helps
    # status-filtered queries.
    op.create_index("ix_wfruns_org_created", "workflow_runs", ["org_id", "created_at"])
    # The engine writes at most one MatchResult per (run, entity) — enforce it.
    # Dedupe first: keep the earliest row per pair (ULIDs are time-ordered,
    # so min(id) is the first written) in case any historical dupes exist.
    op.execute(
        """
        DELETE FROM match_results mr
        USING match_results keeper
        WHERE keeper.match_run_id = mr.match_run_id
          AND keeper.entity_id = mr.entity_id
          AND keeper.id < mr.id
        """
    )
    op.create_index(
        "uq_matchresult_run_entity", "match_results", ["match_run_id", "entity_id"], unique=True
    )
    # NOTE: ix_evidence_org_user (org_id, user_id) deliberately NOT created —
    # ix_evidence_user_cap (org_id, user_id, capability_key) already covers
    # that prefix.


def downgrade() -> None:
    op.drop_index("uq_matchresult_run_entity", table_name="match_results")
    op.drop_index("ix_wfruns_org_created", table_name="workflow_runs")
    op.drop_index("ix_creator_assignments_org", table_name="creator_assignments")
