"""Copy to clipboard — generate copyable content for various contexts."""

import html


def format_for_copy(*, content: str, format_type: str = "plain") -> dict:
    formats = {
        "plain": content,
        "markdown": f"```\n{content}\n```",
        "html": f"<pre><code>{html.escape(content)}</code></pre>",
        "curl": f"curl -X GET '{content}'",
        "env": f'export API_KEY="{content}"',
    }
    if format_type not in formats:
        return {"error": f"Unknown format. Valid: {', '.join(sorted(formats))}"}
    return {"formatted": formats[format_type], "format": format_type,
            "char_count": len(formats[format_type])}


def generate_share_text(*, app_name: str, app_url: str, tagline: str) -> dict:
    twitter = f"Check out {app_name} on @OpenSkill! {tagline} {app_url}"
    linkedin = f"I'm using {app_name} - {tagline}. Check it out: {app_url}"
    email_subject = f"Check out {app_name}"
    email_body = f"Hi,\n\nI thought you'd be interested in {app_name}.\n\n{tagline}\n\n{app_url}"
    return {
        "twitter": twitter,
        "linkedin": linkedin,
        "email": {"subject": email_subject, "body": email_body},
        "plain": f"{app_name} - {tagline} | {app_url}",
    }
