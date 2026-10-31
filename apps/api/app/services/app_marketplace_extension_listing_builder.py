"""Extension Listing Builder — structured builder for marketplace listings."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ExtensionListing:
    extension_id: str
    name: str = ""
    tagline: str = ""
    description: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    icon_url: str = ""
    screenshots: list[str] = field(default_factory=list)
    pricing: str = "free"
    website: str = ""
    support_url: str = ""
    privacy_policy_url: str = ""
    draft: bool = True

    def completeness(self) -> int:
        fields = [self.name, self.tagline, self.description, self.category,
                  self.icon_url, self.pricing]
        filled = sum(1 for f in fields if f)
        if self.tags: filled += 1
        if self.screenshots: filled += 1
        return round(filled / 8 * 100)

    def validate(self) -> list[str]:
        errors = []
        if not self.name: errors.append("Name is required")
        if len(self.name) > 50: errors.append("Name too long (max 50)")
        if not self.tagline: errors.append("Tagline is required")
        if not self.description: errors.append("Description is required")
        if len(self.description) < 20: errors.append("Description too short (min 20)")
        if not self.category: errors.append("Category is required")
        return errors


class ExtListingBuilderService:
    def __init__(self):
        self._listings: dict[str, ExtensionListing] = {}

    def create(self, extension_id: str) -> ExtensionListing:
        listing = ExtensionListing(extension_id=extension_id)
        self._listings[extension_id] = listing
        return listing

    def update(self, extension_id: str, **kwargs) -> bool:
        listing = self._listings.get(extension_id)
        if not listing: return False
        for k, v in kwargs.items():
            if hasattr(listing, k):
                setattr(listing, k, v)
        return True

    def publish(self, extension_id: str) -> tuple[bool, list[str]]:
        listing = self._listings.get(extension_id)
        if not listing: return False, ["Listing not found"]
        errors = listing.validate()
        if errors: return False, errors
        listing.draft = False
        return True, []

    def get(self, extension_id: str) -> ExtensionListing | None:
        return self._listings.get(extension_id)
