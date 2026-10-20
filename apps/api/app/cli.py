"""CLI management commands — bootstrap admin, seed data, etc.

Usage:
    cd apps/api && uv run python -m app.cli create-admin
"""

import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus


async def _create_admin(email: str, password: str, name: str) -> None:
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if an admin already exists with this email
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            if existing.role == UserRole.ADMIN:
                print(f"Admin user '{email}' already exists.")
                return
            # Promote existing user
            existing.role = UserRole.ADMIN
            existing.status = UserStatus.ACTIVE
            await session.commit()
            print(f"Promoted existing user '{email}' to ADMIN.")
            return

        from ulid import ULID

        user = User(
            id=str(ULID()),
            email=email,
            email_verified=True,
            password_hash=hash_password(password),
            display_name=name,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        await session.commit()
        print(f"Created admin user '{email}' (id={user.id}).")

    await engine.dispose()


async def _run_sweep(name: str) -> None:
    from app.controlplane.services import metering
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as db:
        if name == "storage":
            n = await metering.sweep_storage(db)
        elif name == "seats":
            n = await metering.sweep_seats(db)
        else:
            n = await metering.flush_api_request_counters(db)
        await db.commit()
        print(f"sweep-{name}: {n} usage events emitted")
    await engine.dispose()


# ── Ecosystem: curated starter sources (Issue #35, ADR-016 §17) ──

# Well-known public feeds an operator would otherwise hand-enter on day 1.
# All start PAUSED: an operator must review, attest robots/ToS compliance for
# their jurisdiction, and explicitly activate each one — seeding never grants
# itself permission to fetch anything.
ECO_STARTER_SOURCES = [
    {
        "name": "Hugging Face — text-to-image models",
        "source_type": "huggingface",
        "trust_level": "community",
        "adapter_key": "huggingface",
        "base_url": "https://huggingface.co/api/models?pipeline_tag=text-to-image&sort=downloads&limit=50",
        "sync_interval_minutes": 1440,
    },
    {
        "name": "Hugging Face — image-to-video models",
        "source_type": "huggingface",
        "trust_level": "community",
        "adapter_key": "huggingface",
        "base_url": "https://huggingface.co/api/models?pipeline_tag=image-to-video&sort=downloads&limit=50",
        "sync_interval_minutes": 1440,
    },
    {
        "name": "ComfyUI releases (GitHub)",
        "source_type": "github_repo",
        "trust_level": "official",
        "adapter_key": "github_releases",
        "base_url": "https://api.github.com/repos/comfyanonymous/ComfyUI/releases?per_page=20",
        "config": {"repo": "comfyanonymous/ComfyUI"},
        "sync_interval_minutes": 720,
    },
    {
        "name": "Internal analyst desk",
        "source_type": "manual_analyst",
        "trust_level": "internal",
        "adapter_key": "manual",
        "base_url": None,
        "sync_interval_minutes": 43200,
    },
]


async def _eco_seed_sources() -> None:
    from app.ecosystem.models.source import EcosystemSource
    from app.ecosystem.services.sources import SourceService

    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        svc = SourceService(session)
        created, skipped = 0, 0
        for spec in ECO_STARTER_SOURCES:
            existing = await session.scalar(
                select(EcosystemSource).where(EcosystemSource.name == spec["name"])
            )
            if existing:
                skipped += 1
                continue
            source = await svc.create(
                name=spec["name"],
                source_type=spec["source_type"],
                trust_level=spec["trust_level"],
                adapter_key=spec["adapter_key"],
                base_url=spec.get("base_url"),
                config=spec.get("config") or {},
                sync_interval_minutes=spec["sync_interval_minutes"],
                robots_compliant=True,
            )
            # Never auto-fetch: operator reviews + activates explicitly
            source.status = "paused"
            created += 1
        await session.commit()
        print(f"Ecosystem starter sources: {created} created (PAUSED), {skipped} already present.")
        print("Review each source, confirm robots/ToS compliance, then activate it.")
    await engine.dispose()


async def _reencrypt_credentials() -> None:
    """R575: after a Fernet key rotation (prepend to CREDENTIAL_ENCRYPTION_KEY),
    re-encrypt every encrypted-at-rest row under the NEWEST key so the old
    key can be dropped. Idempotent — rows already on the newest key still
    decrypt and re-encrypt cleanly. Covers: connection credentials (bumps
    key_version), webhook signing secrets (current + prev), OIDC client
    secrets, LTI tool private keys, workflow provider credentials."""
    from sqlalchemy import select

    from app.core.crypto import (
        current_key_generation,
        decrypt_credentials,
        decrypt_secret_tolerant,
        encrypt_credentials,
        encrypt_secret,
    )
    from app.core.database import AsyncSessionLocal, engine
    from app.integrations.models import SsoConnection
    from app.integrations.models.connection import IntegrationConnectionCredential
    from app.integrations.models.lti import LtiRegistration
    from app.models.provider import OrgCredential
    from app.models.webhook import WebhookSubscription

    gen = current_key_generation()
    counts: dict[str, int] = {}
    stuck: dict[str, list[str]] = {}

    def _note(kind: str, row_id: str) -> None:
        stuck.setdefault(kind, []).append(row_id)

    async with AsyncSessionLocal() as db:
        for cred in (await db.execute(select(IntegrationConnectionCredential))).scalars():
            # Per-row tolerance: a row encrypted under a key that is no
            # longer configured (lost key, test debris) is REPORTED, never a
            # sweep-stopping crash — the owner must re-enter that credential.
            try:
                cred.ciphertext = encrypt_credentials(decrypt_credentials(cred.ciphertext))
            except Exception:  # noqa: BLE001
                _note("connection_credentials", cred.connection_id)
                continue
            cred.key_version = gen
            counts["connection_credentials"] = counts.get("connection_credentials", 0) + 1
        for sub in (await db.execute(select(WebhookSubscription))).scalars():
            # decrypt_secret_tolerant passes legacy plaintext through and
            # never raises — webhook secrets cannot get stuck.
            sub.secret = encrypt_secret(decrypt_secret_tolerant(sub.secret))
            if sub.secret_prev:
                sub.secret_prev = encrypt_secret(decrypt_secret_tolerant(sub.secret_prev))
            counts["webhook_secrets"] = counts.get("webhook_secrets", 0) + 1
        for conn in (
            await db.execute(
                select(SsoConnection).where(SsoConnection.oidc_client_secret_ct.is_not(None))
            )
        ).scalars():
            try:
                conn.oidc_client_secret_ct = encrypt_credentials(
                    decrypt_credentials(conn.oidc_client_secret_ct)
                )
                counts["oidc_client_secrets"] = counts.get("oidc_client_secrets", 0) + 1
            except Exception:  # noqa: BLE001
                _note("oidc_client_secrets", conn.id)
        for reg in (await db.execute(select(LtiRegistration))).scalars():
            try:
                reg.private_pem_ct = encrypt_credentials(decrypt_credentials(reg.private_pem_ct))
                counts["lti_private_keys"] = counts.get("lti_private_keys", 0) + 1
            except Exception:  # noqa: BLE001
                _note("lti_private_keys", reg.id)
        for pc in (await db.execute(select(OrgCredential))).scalars():
            try:
                pc.encrypted_data = encrypt_credentials(decrypt_credentials(pc.encrypted_data))
                counts["org_credentials"] = counts.get("org_credentials", 0) + 1
            except Exception:  # noqa: BLE001
                _note("org_credentials", pc.id)
        await db.commit()
    await engine.dispose()
    print(f"re-encrypted under key generation {gen}:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    if not counts:
        print("  (no encrypted rows found)")
    for kind, ids in sorted(stuck.items()):
        print(f"  UNDECRYPTABLE {kind}: {len(ids)} row(s) — re-enter these: {ids[:10]}")
    if stuck:
        sys.exit(2)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <command>")
        print("Commands:")
        print("  create-admin   Create or promote an admin user")
        print("  sweep-storage  Emit storage_gb_day usage events (Issue #27)")
        print("  sweep-seats    Emit active_learner_seat usage events")
        print("  flush-api      Land Redis api_request counters as usage events")
        print("  reencrypt-credentials  Re-encrypt all secrets under the newest Fernet key (R575)")
        sys.exit(1)

    command = sys.argv[1]

    if command in ("sweep-storage", "sweep-seats", "flush-api"):
        asyncio.run(_run_sweep(command.removeprefix("sweep-").removeprefix("flush-")))
        return

    if command == "reencrypt-credentials":
        asyncio.run(_reencrypt_credentials())
        return

    if command == "eco-seed":
        asyncio.run(_eco_seed_sources())
        return

    if command == "create-admin":
        email = os.environ.get("ADMIN_EMAIL") or input("Admin email: ").strip()
        password = os.environ.get("ADMIN_PASSWORD") or input("Admin password: ").strip()
        name = os.environ.get("ADMIN_NAME", "Admin")

        if not email or not password:
            print("Error: email and password are required.")
            print("Set ADMIN_EMAIL and ADMIN_PASSWORD env vars, or enter them interactively.")
            sys.exit(1)

        if len(password) < 8:
            print("Error: password must be at least 8 characters.")
            sys.exit(1)

        asyncio.run(_create_admin(email, password, name))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
