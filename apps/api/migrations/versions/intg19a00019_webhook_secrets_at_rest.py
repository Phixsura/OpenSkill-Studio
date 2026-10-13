"""R371: webhook signing secrets encrypted at rest. A DB dump previously
handed an attacker every org's delivery-forging key (plaintext String(64)).
Widen the columns for Fernet ciphertext and encrypt existing rows in place;
the read path tolerates legacy plaintext, so downgrade only re-widens —
already-encrypted rows keep decrypting via decrypt_secret_tolerant.

Revision ID: intg19a00019
Revises: intg18a00018
Create Date: 2026-10-13
"""

import sqlalchemy as sa
from alembic import op

revision = "intg19a00019"
down_revision = "intg18a00018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "webhook_subscriptions",
        "secret",
        existing_type=sa.String(64),
        type_=sa.String(255),
        existing_nullable=False,
    )
    op.alter_column(
        "webhook_subscriptions",
        "secret_prev",
        existing_type=sa.String(64),
        type_=sa.String(255),
        existing_nullable=True,
    )
    # Encrypt existing plaintext rows in place. Fernet tokens start with
    # "gAAAA" and are >100 chars; legacy plaintext is 64 hex chars, so the
    # length guard makes the data migration idempotent.
    from app.core.crypto import encrypt_secret

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT id, secret, secret_prev FROM webhook_subscriptions "
            "WHERE length(secret) <= 64 OR (secret_prev IS NOT NULL AND length(secret_prev) <= 64)"
        )
    ).fetchall()
    for row in rows:
        updates = {}
        if row.secret and len(row.secret) <= 64:
            updates["secret"] = encrypt_secret(row.secret)
        if row.secret_prev and len(row.secret_prev) <= 64:
            updates["secret_prev"] = encrypt_secret(row.secret_prev)
        if updates:
            sets = ", ".join(f"{k} = :{k}" for k in updates)
            conn.execute(
                sa.text(f"UPDATE webhook_subscriptions SET {sets} WHERE id = :id"),
                {**updates, "id": row.id},
            )


def downgrade() -> None:
    # Ciphertext cannot shrink back to 64 chars; keep width, columns stay
    # compatible (tolerant read handles both forms).
    pass
