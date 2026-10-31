"""Changelog parser — parse CHANGELOG.md into structured data."""

import re
import html

VERSION_RE = re.compile(r"^##\s+\[?v?(\d+\.\d+\.\d+)\]?\s*[-—]?\s*(.*)?$")
ENTRY_RE = re.compile(r"^[-*]\s+(.+)$")


def parse_changelog(*, markdown: str) -> dict:
    releases = []
    current = None
    for line in markdown.splitlines():
        vm = VERSION_RE.match(line.strip())
        if vm:
            if current:
                releases.append(current)
            current = {"version": vm.group(1), "date": vm.group(2).strip() or None, "entries": []}
            continue
        if current is not None:
            em = ENTRY_RE.match(line.strip())
            if em:
                text = em.group(1)
                entry_type = "fix" if text.lower().startswith("fix") else "feat" if any(w in text.lower() for w in ("add", "new", "feat")) else "other"
                current["entries"].append({"text": html.escape(text), "type": entry_type})
    if current:
        releases.append(current)
    return {"releases": releases, "total_releases": len(releases),
            "total_entries": sum(len(r["entries"]) for r in releases),
            "latest": releases[0]["version"] if releases else None}
