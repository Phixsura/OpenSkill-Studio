"""Share modal — generate sharing options for apps."""

import html
from urllib.parse import quote


def build_share_options(*, app_name: str, app_url: str, description: str) -> dict:
    safe_name = html.escape(app_name)
    enc_url = quote(app_url, safe="")
    enc_text = quote(f"Check out {app_name} — {description[:100]}", safe="")
    return {
        "app_name": safe_name,
        "url": app_url,
        "platforms": [
            {"id": "twitter", "label": "Twitter / X", "icon": "𝕏",
             "url": f"https://twitter.com/intent/tweet?url={enc_url}&text={enc_text}"},
            {"id": "linkedin", "label": "LinkedIn", "icon": "in",
             "url": f"https://linkedin.com/sharing/share-offsite/?url={enc_url}"},
            {"id": "email", "label": "Email", "icon": "📧",
             "url": f"mailto:?subject={quote(app_name)}&body={enc_text}%20{enc_url}"},
        ],
        "copy_url": app_url,
        "embed_code": f'<a href="{html.escape(app_url)}">{safe_name} on OpenSkill</a>',
    }
