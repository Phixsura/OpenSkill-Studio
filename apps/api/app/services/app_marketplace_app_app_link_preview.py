"""Link preview — generate rich link previews for shared URLs."""

import html


def generate_link_preview(*, url: str, title: str, description: str,
                            image_url: str | None = None, site_name: str = "OpenSkill") -> dict:
    safe_title = html.escape(title[:100])
    safe_desc = html.escape(description[:200])
    domain = url.split("//")[-1].split("/")[0] if "//" in url else url.split("/")[0]
    return {
        "url": url,
        "title": safe_title,
        "description": safe_desc,
        "image_url": image_url,
        "site_name": site_name,
        "domain": domain,
        "has_image": image_url is not None,
    }
