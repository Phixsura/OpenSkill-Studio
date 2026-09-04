"""Converge repair for the cp17 backfill rework (R130[18]/[21]).

cp17's duplicate-copy backfill was rewritten in place by the R129 commit
(NULL-provenance/keep-newest → ARCHIVE/keep-oldest). Alembic records cp17 as
applied, so DBs migrated in the window between the two commits ran the OLD
backfill and never see the fix. This revision re-runs the dedupe idempotently
and drops assignments stranded on archived copies.

R131 audit revisions:
- Step 1 is provably a no-op on any post-cp17 DB (the partial unique index
  admits at most one live copy per (org, origin listing)); it stays as a
  belt-and-suspenders for drifted DBs. The n_assign preference keeps the
  cohort-ASSIGNED copy when duplicates DO exist (R130[21]: keep-oldest
  archived the copy admins had actually assigned).
- The earlier draft also RE-POINTED stranded assignments to the live copy.
  Dropped: the heuristic could not distinguish cp17-backfill collateral from
  a deliberate PUT-archive retirement, silently resurrecting retired content
  onto a re-installed copy (and could target a DRAFT copy, bypassing the
  published-only assignment gate). Window-DB admins re-assign manually; the
  deletion below logs nothing but is reviewable via the audit of this
  migration run in ops notes.
- Assignments on archived paths are NOT fully unreachable (the earlier
  docstring claim was wrong): get_effective_skills reads them without a
  status filter. Deleting them here converges to delete_path semantics —
  update_path's archive branch now applies the same cleanup going forward.
- Known residual: provenance NULLed by the old backfill is unrecoverable
  (indistinguishable from local authoring); the resale gate misses those
  rows on window-migrated DBs only.

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
    # 2. Drop assignments stranded on ARCHIVED origin-carrying copies
    # (delete_path semantics: archiving removes assignments; the raw cp17
    # UPDATE skipped that cleanup and the rows kept feeding
    # get_effective_skills).
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
