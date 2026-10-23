"""Documentation renderer — parse markdown docs with frontmatter and TOC."""
from __future__ import annotations
import html
import re


def parse_doc(content: str) -> dict:
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip()
            body = parts[2].strip()
    headings = []
    for m in re.finditer(r"^(#{1,4})\s+(.+)$", body, re.MULTILINE):
        level = len(m.group(1))
        text = m.group(2).strip()
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        headings.append({"level": level, "text": html.escape(text), "slug": slug})
    word_count = len(body.split())
    read_time = max(1, round(word_count / 200))
    return {
        "frontmatter": frontmatter, "headings": headings,
        "body": body, "word_count": word_count,
        "read_time_min": read_time, "read_time_display": f"{read_time} min read",
        "has_toc": len(headings) > 2,
    }
