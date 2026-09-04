"""Converge repair for the cp17 backfill rework (R130[18]/[21]).

cp17's duplicate-copy backfill was rewritten in place by the R129 commit
(NULL-provenance/keep-newest → ARCHIVE/keep-oldest). Alembic records cp17 as
applied, so DBs migrated in the window between the two commits ran the OLD
backfill and never see the fix. This revision re-runs the repair idempotently
and heals the collateral the raw ARCHIVE left behind:

1. Re-archive live duplicate copies per (org, origin listing) — preferring
   the copy that carries cohort assignments (R130[21]: keep-OLDEST archived
   the copy admins had actually assigned), then the oldest.
2. Re-point cohort assignments stranded on archived duplicates to the live
   copy of the same (org, origin) — the service's delete_path always removes
   assignments when archiving, so any assignment on an ARCHIVED path is an
   orphan no API can reach (list filters it; unassign 404s on get_path).
3. Provenance NULLed by the old backfill is unrecoverable (the listing link
   is gone); such rows are indistinguishable from local authoring. Known
   residual for window-migrated DBs only — the resale gate misses them.

Revision ID: cp19b0000019
Revises: cp18a0000018
"""

import sqlalchemy as sa
from alembic import op

revision = "cp19b0000019"
down_revision = "cp18a0000018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Idempotent dedupe: keep the assigned copy first, then the oldest.
    op.execute(
        sa.text(
            """
            UPDATE learning_paths lp SET status = 'ARCHIVED'
            WHERE lp.origin_listing_id IS NOT NULL
              AND lp.status != 'ARCHIVED'
              AND lp.id NOT IN (
                SELECT DISTINCT ON (org_id, origin_listing_id) id FROM (
                  SELECT p.id, p.org_id, p.origin_listing_id, p.created_at,
                         (SELECT count(*)
                          FROM cohort_learning_path_assignments a
                          WHERE a.path_id = p.id) AS n_assign
                  FROM learning_paths p
                  WHERE p.origin_listing_id IS NOT NULL
                    AND p.status != 'ARCHIVED'
                ) t
                ORDER BY org_id, origin_listing_id, n_assign DESC, created_at ASC
              )
            """
        )
    )
    # 2a. Re-point stranded assignments to the surviving live copy.
    op.execute(
        sa.text(
            """
            INSERT INTO cohort_learning_path_assignments
                (cohort_id, path_id, assigned_at, assigned_by)
            SELECT a.cohort_id, live.id, a.assigned_at, a.assigned_by
            FROM cohort_learning_path_assignments a
            JOIN learning_paths dead
              ON dead.id = a.path_id
             AND dead.status = 'ARCHIVED'
             AND dead.origin_listing_id IS NOT NULL
            JOIN learning_paths live
              ON live.org_id = dead.org_id
             AND live.origin_listing_id = dead.origin_listing_id
             AND live.status != 'ARCHIVED'
            ON CONFLICT DO NOTHING
            """
        )
    )
    # 2b. Drop the orphans (service semantics: archiving removes assignments).
    op.execute(
        sa.text(
            """
            DELETE FROM cohort_learning_path_assignments a
            USING learning_paths dead
            WHERE dead.id = a.path_id
              AND dead.status = 'ARCHIVED'
              AND dead.origin_listing_id IS NOT NULL
            """
        )
    )


def downgrade() -> None:
    # Data repair — nothing structural to reverse.
    pass
