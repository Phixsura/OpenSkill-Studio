"""Capability ontology — platform-level talent capability graph (ADR-015 D1).

Separate from CapabilityTag (ADR-011 workflow I/O taxonomy). Capabilities
represent demonstrable human skills; CapabilityTags represent workflow step
contracts. A capability MAY link to a tag when the concepts overlap.
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# ---------------------------------------------------------------------------
# Core capability node
# ---------------------------------------------------------------------------


class Capability(Base):
    """A named human capability in the talent ontology."""

    __tablename__ = "capabilities"


    def __repr__(self) -> str:
        return f"<Capability {self.id}>"

    id: Mapped[str] = ulid_pk()
    canonical_name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # visual_design | production | communication | workflow_design |
    # ai_fundamentals | business
    category: Mapped[str] = mapped_column(String(40))
    parent_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="SET NULL"), nullable=True
    )
    # active | deprecated | merged | archived
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    # When status=merged, the successor capability
    merged_into_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="SET NULL"), nullable=True
    )
    # Bridge to workflow I/O taxonomy (CapabilityTag)
    capability_tag_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("capability_tags.id", ondelete="SET NULL"), nullable=True
    )
    # Per-family level definition overrides (NULL = use platform defaults)
    # {"1": {"label": "...", "min_score": 0.2, "min_evidence": 1}, ...}
    level_definitions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Decay configuration: {"half_life_days": 365}  (NULL = no decay)
    decay_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # External taxonomy crosswalks: {"esco_uri": "http://...", "onet_code": "15-1252.00", "isced_f": "0613"}
    external_ids: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Alternative names / synonyms for search and deduplication
    aliases: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Multilingual names: {"zh": {"name": "...", "description": "..."}, "en": {...}}
    translations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_capabilities_category", "category"),
        Index("ix_capabilities_parent", "parent_id"),
        Index("ix_capabilities_status", "status"),
    )


# ---------------------------------------------------------------------------
# Typed directed edges between capabilities
# ---------------------------------------------------------------------------

# Allowed edge types — validated at service level, not DB enum (extensible)
EDGE_TYPES = frozenset(
    {"requires", "related_to", "specializes", "subsumes", "commonly_paired_with"}
)


class CapabilityEdge(Base):
    """Typed directed relationship between two capabilities."""

    __tablename__ = "capability_edges"


    def __repr__(self) -> str:
        return f"<CapabilityEdge {self.id}>"

    id: Mapped[str] = ulid_pk()
    source_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    target_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    # requires | related_to | specializes | subsumes | commonly_paired_with
    edge_type: Mapped[str] = mapped_column(String(30))
    extra: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("uq_capability_edge", "source_id", "target_id", "edge_type", unique=True),
        Index("ix_capability_edges_target", "target_id"),
        CheckConstraint("source_id != target_id", name="ck_capability_no_self_loop"),
    )


# ---------------------------------------------------------------------------
# Content-to-capability mappings
# ---------------------------------------------------------------------------

# Allowed source types for mappings
MAPPING_SOURCE_TYPES = frozenset(
    {
        "skill",
        "skill_pack",
        "project_template",
        "workflow_pack",
        "rubric_criterion",
        "assessment_blueprint",
        "commercial_project",
    }
)


class CapabilityMapping(Base):
    """Maps platform content to a capability with a contribution weight."""

    __tablename__ = "capability_mappings"


    def __repr__(self) -> str:
        return f"<CapabilityMapping {self.id}>"

    id: Mapped[str] = ulid_pk()
    capability_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )
    source_type: Mapped[str] = mapped_column(String(30))
    source_id: Mapped[str] = mapped_column(String(26))
    # 0.0–1.0: how much this source contributes to the capability
    contribution_weight: Mapped[float] = mapped_column(
        Numeric(3, 2), default=1.0, server_default="1.00"
    )
    # primary_instruction | practice | assessment | incidental
    evidence_type: Mapped[str] = mapped_column(
        String(30), default="primary_instruction", server_default="'primary_instruction'"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("uq_cap_mapping", "capability_id", "source_type", "source_id", unique=True),
        Index("ix_cap_mapping_source", "source_type", "source_id"),
        CheckConstraint(
            "contribution_weight >= 0 AND contribution_weight <= 1",
            name="ck_contribution_weight_range",
        ),
    )
