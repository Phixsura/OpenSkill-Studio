"""Employer / opportunity models — structured job postings (ADR-015 D6).

Employers are Organizations with org_type='employer'. EmployerProfile adds
employer-specific metadata as a satellite table.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class EmployerProfile(Base):
    """Employer-specific metadata on an Organization."""

    __tablename__ = "employer_profiles"

    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    company_size: Mapped[str | None] = mapped_column(String(30), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Employer branding fields (I6)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    culture_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    values: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    social_links: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # verified | pending | unverified
    verification_status: Mapped[str] = mapped_column(
        String(20), default="unverified", server_default="'unverified'"
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Opportunity(Base):
    """A structured internship/job/project-role posting."""

    __tablename__ = "opportunities"

    id: Mapped[str] = ulid_pk()
    employer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # internship | full_time | part_time | contract | freelance |
    # project_role | apprenticeship | campus_project
    opportunity_type: Mapped[str] = mapped_column(String(30))
    # remote | onsite | hybrid
    location_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    compensation_display: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # [{"capability_id": "01J...", "min_level": 3, "required": true}]
    required_capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # [{"capability_id": "01J...", "min_level": 2, "required": false}]
    preferred_capabilities: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # Minimum verification level for evidence
    minimum_verification: Mapped[str | None] = mapped_column(String(30), nullable=True)
    portfolio_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    openings: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    # draft | open | closed | filled | cancelled
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="'draft'")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_opportunities_employer", "employer_org_id", "status"),
        Index("ix_opportunities_type", "opportunity_type", "status"),
        Index("ix_opportunities_deadline", "application_deadline"),
    )
