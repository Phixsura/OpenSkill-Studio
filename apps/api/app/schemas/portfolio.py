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
        if v is not None and v != "":
            if len(v) > 500:
                raise ValueError("URL must be 500 characters or less")
            if not re.match(r"^https?://", v, re.IGNORECASE):
                raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Headline must be 200 characters or less")
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 5000:
            raise ValueError("Bio must be 5,000 characters or less")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Location must be 200 characters or less")
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str | None) -> str | None:
        if v is not None and v not in {"public", "private"}:
            raise ValueError("visibility must be one of: public, private")
        return v

    @field_validator("social_links")
    @classmethod
    def validate_social_links(cls, v: dict | None) -> dict | None:
        if v is not None:
            if len(v) > 20:
                raise ValueError("At most 20 social links")
            for key, url in v.items():
                if not isinstance(key, str) or len(key) > 50:
                    raise ValueError("Social link keys must be strings of 50 chars or less")
                if not isinstance(url, str) or len(url) > 500:
                    raise ValueError(f"Social link '{key}' must be a URL of 500 chars or less")
                if not re.match(r"^https?://", url, re.IGNORECASE):
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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            cleaned = [t.strip() for t in v if isinstance(t, str) and t.strip()]
            if len(cleaned) > 30:
                raise ValueError("At most 30 tags")
            for t in cleaned:
                if len(t) > 50:
                    raise ValueError("Each tag must be 50 characters or less")
            return cleaned
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 200:
            raise ValueError("Title must be 2-200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v

    @field_validator("external_url", "cover_image_url")
    @classmethod
    def validate_urls(cls, v: str | None) -> str | None:
        if v is not None and v != "":
            if len(v) > 500:
                raise ValueError("URL must be 500 characters or less")
            if not re.match(r"^https?://", v, re.IGNORECASE):
                raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        if v not in {"public", "unlisted", "private"}:
            raise ValueError("visibility must be one of: public, unlisted, private")
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

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 200:
            raise ValueError("Title must not exceed 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")
        return v

    @field_validator("cover_image_url")
    @classmethod
    def validate_cover_image_url(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Cover Image Url must not exceed 500 characters")
        return v

    @field_validator("external_url")
    @classmethod
    def validate_external_url(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("External Url must not exceed 500 characters")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            cleaned = [t.strip() for t in v if isinstance(t, str) and t.strip()]
            if len(cleaned) > 30:
                raise ValueError("At most 30 tags")
            for t in cleaned:
                if len(t) > 50:
                    raise ValueError("Each tag must be 50 characters or less")
            return cleaned
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str | None) -> str | None:
        if v is not None and v not in {"public", "unlisted", "private"}:
            raise ValueError("visibility must be one of: public, unlisted, private")
        return v


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


class ReorderItemsRequest(BaseModel):
    item_ids: list[str]

    @field_validator("item_ids")
    @classmethod
    def validate_item_ids(cls, v: list) -> list:
        if len(v) > 500:
            raise ValueError("Too many items to reorder")
        for iid in v:
            if not isinstance(iid, str):
                raise ValueError("item_ids must be a list of strings")
        return v
