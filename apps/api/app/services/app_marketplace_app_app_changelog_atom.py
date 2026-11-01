"""Changelog Atom — generate Atom feed for app changelogs."""

from xml.sax.saxutils import escape
from datetime import datetime


def generate_atom_feed(*, app_name: str, app_id: str, entries: list[dict],
                         base_url: str = "https://marketplace.openskill.dev") -> dict:
    safe_name = escape(app_name)
    safe_base = escape(base_url)
    items_xml = []
    for entry in entries:
        items_xml.append(
            f"  <entry>\n"
            f"    <title>{escape(entry.get('title', ''))}</title>\n"
            f"    <id>{safe_base}/apps/{escape(app_id)}/changelog/{escape(entry.get('version', ''))}</id>\n"
            f"    <updated>{escape(entry.get('date', ''))}</updated>\n"
            f"    <summary>{escape(entry.get('summary', ''))}</summary>\n"
            f"  </entry>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f'  <title>{safe_name} Changelog</title>\n'
        f'  <link href="{safe_base}/apps/{escape(app_id)}"/>\n'
        f'  <id>{safe_base}/apps/{escape(app_id)}/feed</id>\n'
        f'  <updated>{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>\n'
        + "\n".join(items_xml) + "\n"
        '</feed>'
    )
    return {"xml": xml, "content_type": "application/atom+xml",
            "entry_count": len(entries)}
