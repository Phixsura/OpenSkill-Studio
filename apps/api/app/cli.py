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


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <command>")
        print("Commands:")
        print("  create-admin   Create or promote an admin user")
        print("  sweep-storage  Emit storage_gb_day usage events (Issue #27)")
        print("  sweep-seats    Emit active_learner_seat usage events")
        print("  flush-api      Land Redis api_request counters as usage events")
        sys.exit(1)

    command = sys.argv[1]

    if command in ("sweep-storage", "sweep-seats", "flush-api"):
        asyncio.run(_run_sweep(command.removeprefix("sweep-").removeprefix("flush-")))
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
