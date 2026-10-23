"""Link checker — validate URLs in app documentation."""

import html
import re
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>\"']+")


def extract_links(*, text: str) -> list[str]:
    return URL_RE.findall(text)


def validate_links(*, urls: list[str]) -> dict:
    results = []
    valid = broken = 0
    for url in urls:
        parsed = urlparse(url)
        is_valid = parsed.scheme in ("https", "http") and bool(parsed.netloc)
        if is_valid:
            valid += 1
            results.append({"url": html.escape(url), "valid": True, "status": "ok"})
        else:
            broken += 1
            results.append({"url": html.escape(url), "valid": False, "status": "invalid_format"})
    return {"results": results, "total": len(results), "valid": valid, "broken": broken,
            "health": "good" if broken == 0 else "warning" if broken < 3 else "critical"}


def scan_markdown(*, markdown: str) -> dict:
    urls = extract_links(text=markdown)
    return validate_links(urls=urls)
