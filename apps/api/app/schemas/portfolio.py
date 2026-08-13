import re
from datetime import datetime

from pydantic import BaseModel, field_validator

RESERVED_USERNAMES = frozenset(
    {
        "admin",
        "api",
        "app",
        "auth",
        "blog",
        "dashboard",
        "docs",
        "help",
        "login",
        "logout",
        "register",
        "settings",
        "status",
        "support",
        "www",
        "health",
        "about",
        "pricing",
        "terms",
        "privacy",
        "u",
        "orgs",
        "join",
        "invite",
    }
)

USERNAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){2,38}[a-z0-9]$")


# ── Profile ──────────────────────────────────────────────


class UpdateProfileRequest(BaseModel):
    headline: str | None = None
    bio: str | None = None
    location: str | None = None
    website_url: str | None = None
    social_links: dict | None = None
    visibility: str | None = None
    theme: str | None = None

    @field_validator("website_url")
    @classmethod
    def validate_website_url(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^https?://", v, re.IGNORECASE):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("social_links")
    @classmethod
    def validate_social_links(cls, v: dict | None) -> dict | None:
        if v is not None:
            for key, url in v.items():
                if not isinstance(url, str) or not re.match(r"^https?://", url, re.IGNORECASE):
                    raise ValueError(f"Social link '{key}' must be a valid http/https URL")
        return v


class UsernameRequest(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.lower().strip()
        if v in RESERVED_USERNAMES:
            raise ValueError("This username is reserved")
        if not USERNAME_PATTERN.match(v):
            raise ValueError("Username must be 4-40 chars, lowercase alphanumeric and hyphens")
        return v


class ProfileResponse(BaseModel):
    user_id: str
    username: str
    headline: str | None
    bio: str | None
    location: str | None
    website_url: str | None
    social_links: dict
    visibility: str
    theme: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicProfileResponse(BaseModel):
    username: str
    display_name: str
    headline: str | None
    bio: str | None
    avatar_url: str | None
    location: str | None
    website_url: str | None
    social_links: dict
    skills: list[dict]
    featured_items: list["PortfolioItemResponse"]
    item_count: int
    joined_at: datetime


# ── Portfolio Items ──────────────────────────────────────


class CreatePortfolioItemRequest(BaseModel):
    submission_id: str | None = None
    title: str
    description: str | None = None
    tags: list[str] | None = None
    cover_image_url: str | None = None
    external_url: str | None = None
    visibility: str = "public"
    featured: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Title must be 2-200 characters")
        return v


class UpdatePortfolioItemRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    cover_image_url: str | None = None
    external_url: str | None = None
    visibility: str | None = None
    featured: bool | None = None
    show_score: bool | None = None


class PortfolioItemResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str | None
    cover_image_url: str | None
    tags: list[str]
    external_url: str | None
    source_org_name: str | None
    source_project: str | None
    score: int | None
    show_score: bool
    visibility: str
    featured: bool
    sort_order: int
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Badges ───────────────────────────────────────────────


class SkillBadgeResponse(BaseModel):
    id: str
    skill_name: str
    category_name: str
    completion_pct: int
    completed: bool
    show_on_profile: bool

    model_config = {"from_attributes": True}


class ToggleBadgeRequest(BaseModel):
    show_on_profile: bool
