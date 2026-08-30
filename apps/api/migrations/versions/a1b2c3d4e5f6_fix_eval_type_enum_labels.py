"""fix eval_type enum labels: lowercase multimodal values → uppercase names

R86: SQLAlchemy's ``Enum(EvalType, ...)`` (no ``values_callable``) persists the
enum MEMBER NAME, not its value. The original three labels were added to the
Postgres ``eval_type`` enum as uppercase names (``EXERCISE_TEXT``,
``EXERCISE_CODE``, ``SUBMISSION_REVIEW``) and work. Migration 65cf240e later
added the four multimodal types as lowercase VALUES
(``image_review``/``video_review``/``prompt_review``/
``commercial_submission_review``), so any INSERT of those members sent the
uppercase NAME (``IMAGE_REVIEW`` …) and hit
``asyncpg.exceptions.InvalidTextRepresentationError: invalid input value for
enum eval_type`` → an unhandled 500 on POST /evaluation/trigger for every
multimodal eval type.

Fix: rename the four lowercase labels to their uppercase names so the whole
enum is consistent with what SQLAlchemy sends. No rows use the lowercase labels
(the 500 always prevented persistence), so RENAME VALUE is safe and in-place.

Revision ID: a1b2c3d4e5f6
Revises: 5b8aba29b5a8
Create Date: 2026-08-30 04:45:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "5b8aba29b5a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (lowercase value that was mistakenly added, uppercase member name SQLAlchemy sends)
_RENAMES = [
    ("image_review", "IMAGE_REVIEW"),
    ("video_review", "VIDEO_REVIEW"),
    ("prompt_review", "PROMPT_REVIEW"),
    ("commercial_submission_review", "COMMERCIAL_SUBMISSION_REVIEW"),
]


def upgrade() -> None:
    # ALTER TYPE ... RENAME VALUE cannot run inside a transaction block on some
    # PG versions; alembic runs each migration in a transaction, but RENAME
    # VALUE is transactional since PG 12 (unlike ADD VALUE), so this is safe.
    # IF EXISTS guard: idempotent if a fresh DB already has the correct labels.
    for old, new in _RENAMES:
        op.execute(
            f"DO $$ BEGIN "
            f"IF EXISTS (SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid "
            f"WHERE t.typname = 'eval_type' AND e.enumlabel = '{old}') THEN "
            f"ALTER TYPE eval_type RENAME VALUE '{old}' TO '{new}'; "
            f"END IF; END $$;"
        )


def downgrade() -> None:
    for old, new in _RENAMES:
        op.execute(
            f"DO $$ BEGIN "
            f"IF EXISTS (SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid "
            f"WHERE t.typname = 'eval_type' AND e.enumlabel = '{new}') THEN "
            f"ALTER TYPE eval_type RENAME VALUE '{new}' TO '{old}'; "
            f"END IF; END $$;"
        )
