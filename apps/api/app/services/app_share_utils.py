"""App share utils — generate share links for marketplace apps."""

from urllib.parse import quote


def build_share_links(*, app_name: str, app_slug: str, base_url: str = "https://marketplace.openskill.studio") -> dict:
    url = f"{base_url}/apps/{app_slug}"
    encoded_url = quote(url)
    encoded_text = quote(f"Check out {app_name} on OpenSkill Marketplace!")
    return {
        "url": url,
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        "email": f"mailto:?subject={quote(f'{app_name} on OpenSkill')}&body={encoded_text}%0A{encoded_url}",
        "copy_text": f"{app_name}: {url}",
    }
