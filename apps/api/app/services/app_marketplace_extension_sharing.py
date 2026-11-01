"""Extension Sharing — share extensions via links, embeds, and social.

Generates shareable links, embed codes, social share URLs, and
tracks share analytics with referral sources.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ShareLink:
    link_id: str
    extension_id: str
    url: str
    embed_code: str
    views: int = 0
    installs_from_share: int = 0


class ExtensionSharingService:
    """Manages extension sharing and referral tracking."""

    BASE_URL = "https://marketplace.openskill.dev/ext"

    def __init__(self):
        self._links: dict[str, ShareLink] = {}
        self._referrals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def create_share_link(self, extension_id: str) -> ShareLink:
        link_id = f"share_{secrets.token_urlsafe(8)}"
        url = f"{self.BASE_URL}/{extension_id}?ref={link_id}"
        embed = f'<iframe src="{self.BASE_URL}/{extension_id}/embed" width="300" height="200"></iframe>'
        link = ShareLink(link_id=link_id, extension_id=extension_id,
                         url=url, embed_code=embed)
        self._links[link_id] = link
        return link

    def record_view(self, link_id: str, source: str = "direct") -> bool:
        link = self._links.get(link_id)
        if link:
            link.views += 1
            self._referrals[link.extension_id][source] += 1
            return True
        return False

    def record_install(self, link_id: str) -> bool:
        link = self._links.get(link_id)
        if link:
            link.installs_from_share += 1
            return True
        return False

    def get_social_urls(self, extension_id: str, name: str) -> dict:
        url = f"{self.BASE_URL}/{extension_id}"
        text = f"Check out {name} on OpenSkill Marketplace!"
        return {
            "twitter": f"https://twitter.com/intent/tweet?text={text}&url={url}",
            "linkedin": f"https://linkedin.com/sharing/share-offsite/?url={url}",
            "copy_link": url,
        }

    def get_referral_stats(self, extension_id: str) -> dict:
        return dict(self._referrals.get(extension_id, {}))

    def get_share_stats(self, link_id: str) -> dict | None:
        link = self._links.get(link_id)
        if not link:
            return None
        conv_rate = round(link.installs_from_share / max(link.views, 1) * 100, 1)
        return {"views": link.views, "installs": link.installs_from_share,
                "conversion_rate": conv_rate}
