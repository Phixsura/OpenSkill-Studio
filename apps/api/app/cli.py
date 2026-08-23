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


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <command>")
        print("Commands:")
        print("  create-admin   Create or promote an admin user")
        sys.exit(1)

    command = sys.argv[1]

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
