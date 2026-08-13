from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


def ulid_pk() -> Mapped[str]:
    """ULID primary key — time-ordered, URL-friendly, no central sequence."""
    return mapped_column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
