"""Badge/credential sharing — generate shareable links and track analytics.

Supports:
  - Direct share URL with UTM tracking
  - LinkedIn "Add to Profile" URL
  - Twitter share URL
  - Email share URL
  - Share/view count tracking
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote, urlencode

# Base URL for public credential verification pages
VERIFY_BASE = "/verify/credential"
PLATFORM_BASE = "https://openskill.studio"

SHARE_PLATFORMS = frozenset({"linkedin", "twitter", "email", "copy"})


@dataclass(frozen=True, slots=True)
class ShareLinks:
    """Generated share links for a credential."""

    credential_id: str
    credential_name: str
    verify_url: str
    linkedin_add_url: str
    linkedin_share_url: str
    twitter_share_url: str
    email_share_url: str
    copy_url: str


def generate_share_links(
    *,
    credential_id: str,
    credential_name: str,
    credential_type: str,
    issuer_name: str = "OpenSkill Studio",
    issued_at: datetime | None = None,
    expires_at: datetime | None = None,
    base_url: str = PLATFORM_BASE,
) -> ShareLinks:
    """Generate all share links for a credential.

    Args:
        credential_id: Credential ULID
        credential_name: Human-readable credential name
        credential_type: Type (e.g., "AI Product Visual — Foundation")
        issuer_name: Issuing organization name
        issued_at: When the credential was issued
        expires_at: When the credential expires (optional)
        base_url: Platform base URL

    Returns:
        ShareLinks with URLs for each platform.
    """
    verify_url = f"{base_url}{VERIFY_BASE}/{credential_id}"

    # LinkedIn "Add to Profile" URL
    # https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME
    linkedin_params: dict[str, str] = {
        "startTask": "CERTIFICATION_NAME",
        "name": credential_name,
        "organizationName": issuer_name,
        "certUrl": verify_url,
        "certId": credential_id,
    }
    if issued_at:
        linkedin_params["issueYear"] = str(issued_at.year)
        linkedin_params["issueMonth"] = str(issued_at.month)
    if expires_at:
        linkedin_params["expirationYear"] = str(expires_at.year)
        linkedin_params["expirationMonth"] = str(expires_at.month)

    linkedin_add_url = f"https://www.linkedin.com/profile/add?{urlencode(linkedin_params)}"

    # LinkedIn share URL
    linkedin_share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(verify_url)}"

    # Twitter share URL
    twitter_text = f"🏆 I earned the {credential_name} credential from {issuer_name}! #{credential_type.replace(' ', '').replace('-', '')} #OpenSkill"
    twitter_share_url = (
        f"https://twitter.com/intent/tweet?text={quote(twitter_text)}&url={quote(verify_url)}"
    )

    # Email share URL
    email_subject = f"My {credential_name} Credential"
    email_body = f"I earned the {credential_name} credential from {issuer_name}.\n\nVerify it here: {verify_url}"
    email_share_url = f"mailto:?subject={quote(email_subject)}&body={quote(email_body)}"

    # Copy URL (just the verify URL with UTM)
    copy_url = f"{verify_url}?utm_source=copy&utm_medium=badge_share"

    return ShareLinks(
        credential_id=credential_id,
        credential_name=credential_name,
        verify_url=verify_url,
        linkedin_add_url=linkedin_add_url,
        linkedin_share_url=linkedin_share_url,
        twitter_share_url=twitter_share_url,
        email_share_url=email_share_url,
        copy_url=copy_url,
    )
