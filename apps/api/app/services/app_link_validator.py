"""App link validator — validate homepage, privacy policy, terms URLs."""

from app.services.app_url_validator import validate_url

def validate_homepage_url(url: str | None) -> list[str]:
    if not url: return []
    return validate_url(url, require_https=True, label="Homepage URL")

def validate_privacy_url(url: str | None) -> list[str]:
    if not url: return []
    return validate_url(url, require_https=True, label="Privacy Policy URL")

def validate_terms_url(url: str | None) -> list[str]:
    if not url: return []
    return validate_url(url, require_https=True, label="Terms of Service URL")

def validate_all_links(*, homepage: str | None = None, privacy: str | None = None, terms: str | None = None) -> list[str]:
    return validate_homepage_url(homepage) + validate_privacy_url(privacy) + validate_terms_url(terms)
