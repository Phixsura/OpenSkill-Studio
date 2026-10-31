"""Input sanitizer — sanitize user input for safe storage and display."""

import re
import html


def sanitize_text(*, text: str, max_length: int = 10000,
                    allow_markdown: bool = False) -> dict:
    # Strip null bytes
    cleaned = text.replace("\x00", "")
    # Limit length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
        truncated = True
    else:
        truncated = False
    # HTML escape
    if not allow_markdown:
        cleaned = html.escape(cleaned)
    else:
        # Even with markdown, strip script tags
        cleaned = re.sub(r"<script[^>]*>.*?</script>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<iframe[^>]*>.*?</iframe>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"on\w+\s*=", "", cleaned, flags=re.IGNORECASE)
    # Strip excessive whitespace
    cleaned = re.sub(r"\n{4,}", "\n\n\n", cleaned)
    return {
        "sanitized": cleaned,
        "original_length": len(text),
        "sanitized_length": len(cleaned),
        "truncated": truncated,
        "modifications": text != cleaned,
    }


def sanitize_url(*, url: str) -> dict:
    safe_schemes = {"http", "https", "mailto"}
    parsed_scheme = url.split(":", 1)[0].lower().strip() if ":" in url else ""
    safe = parsed_scheme in safe_schemes
    return {"url": url if safe else "", "safe": safe,
            "scheme": parsed_scheme, "error": None if safe else "Blocked: unsafe URL scheme"}
