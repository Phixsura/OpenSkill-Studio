"""Pack Category models — taxonomy for organizing skill packs in the registry."""

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class PackCategory(Base):
    __tablename__ = "pack_categories"
    __table_args__ = (Index("uq_pack_category_slug", "slug", unique=True),)

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("pack_categories.id", ondelete="SET NULL")
    )
    icon: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class PackCategoryAssignment(Base):
    """Join: which categories a pack belongs to (composite PK)."""

    __tablename__ = "pack_category_assignments"

    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("pack_categories.id", ondelete="CASCADE"), primary_key=True
    )
