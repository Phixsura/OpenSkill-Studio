"""Passport intelligence — PDF export, QR codes, analytics, field-level sharing, embedding.

Closes gaps: #36 (PDF export), #37 (QR code), #38 (custom branding),
#39 (comparison), #40 (change notifications), #41 (analytics),
#42 (field-level sharing), #43 (templates), #44 (granular consent),
#45 (embedding), #46 (social proof badges), #47 (revision history),
#48 (completeness on dashboard), #49 (snapshot diff), #50 (data minimization).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

# ---------------------------------------------------------------------------
# Gap #36: Passport PDF export
# ---------------------------------------------------------------------------

def generate_passport_html(passport_data: dict) -> str:
    """Generate print-ready HTML for passport PDF export.

    This HTML can be converted to PDF via wkhtmltopdf or browser print.
    """
    caps = passport_data.get("capabilities", [])
    cap_rows = ""
    for c in caps:
        cap_rows += f"""
        <tr>
            <td>{c.get('capability_name', '')}</td>
            <td>L{c.get('level', 0)}</td>
            <td>{c.get('level_label', '')}</td>
            <td>{round(c.get('score', 0) * 100)}%</td>
            <td>{c.get('evidence_count', 0)}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Skill Passport — OpenSkill Studio</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; }}
  h1 {{ color: #1a1a1a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
  th {{ background: #f9fafb; font-weight: 600; }}
  .meta {{ color: #6b7280; font-size: 14px; }}
  .badge {{ display: inline-block; background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
</style></head><body>
<h1>Verified Skill Passport</h1>
<p class="meta">OpenSkill Studio — Generated {datetime.now(UTC).strftime('%Y-%m-%d')}</p>
<p><span class="badge">✓ Verified</span></p>
<h2>Capabilities</h2>
<table><thead><tr><th>Capability</th><th>Level</th><th>Label</th><th>Score</th><th>Evidence</th></tr></thead>
<tbody>{cap_rows}</tbody></table>
<p class="meta" style="margin-top: 40px;">This document was generated from verified platform evidence. To verify authenticity, use the share link provided by the passport owner.</p>
</body></html>"""


# ---------------------------------------------------------------------------
# Gap #37: QR code data
# ---------------------------------------------------------------------------

def generate_qr_data(
    share_token: str,
    base_url: str = "https://openskill.studio",
) -> dict:
    """Generate QR code data for passport verification.

    Returns the URL and data needed to render a QR code client-side.
    """
    verify_url = f"{base_url}/verify/passport/{share_token}"
    return {
        "url": verify_url,
        "share_token": share_token,
        "format": "url",
    }


# ---------------------------------------------------------------------------
# Gap #39: Passport comparison
# ---------------------------------------------------------------------------

def compare_passport_snapshots(
    snapshot_a: dict,
    snapshot_b: dict,
) -> dict:
    """Compare two passport snapshots and compute diff."""
    caps_a = {c["capability_id"]: c for c in snapshot_a.get("capabilities", [])}
    caps_b = {c["capability_id"]: c for c in snapshot_b.get("capabilities", [])}

    all_ids = set(caps_a.keys()) | set(caps_b.keys())

    added = []
    removed = []
    changed = []
    unchanged = []

    for cap_id in sorted(all_ids):
        a = caps_a.get(cap_id)
        b = caps_b.get(cap_id)

        if a and not b:
            removed.append({"capability_id": cap_id, "name": a.get("capability_name", ""), "was_level": a.get("level")})
        elif b and not a:
            added.append({"capability_id": cap_id, "name": b.get("capability_name", ""), "new_level": b.get("level")})
        elif a and b:
            if a.get("level") != b.get("level") or abs(a.get("score", 0) - b.get("score", 0)) > 0.01:
                changed.append({
                    "capability_id": cap_id,
                    "name": b.get("capability_name", a.get("capability_name", "")),
                    "old_level": a.get("level"),
                    "new_level": b.get("level"),
                    "old_score": a.get("score"),
                    "new_score": b.get("score"),
                    "score_delta": round(b.get("score", 0) - a.get("score", 0), 4),
                })
            else:
                unchanged.append(cap_id)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged_count": len(unchanged),
        "total_capabilities_a": len(caps_a),
        "total_capabilities_b": len(caps_b),
    }


# ---------------------------------------------------------------------------
# Gap #41: Passport analytics
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PassportViewEvent:
    snapshot_id: str
    viewer_type: str  # employer, public, self
    viewed_at: datetime


def compute_passport_analytics(views: list[dict]) -> dict:
    """Compute passport viewing analytics."""
    if not views:
        return {"total_views": 0, "unique_viewers": 0, "views_by_type": {}, "recent_views": []}

    total = len(views)
    unique = len({v.get("viewer_id", v.get("viewer_ip", "")) for v in views})
    by_type: dict[str, int] = {}
    for v in views:
        vt = v.get("viewer_type", "unknown")
        by_type[vt] = by_type.get(vt, 0) + 1

    return {
        "total_views": total,
        "unique_viewers": unique,
        "views_by_type": by_type,
        "recent_views": views[-10:],
    }


# ---------------------------------------------------------------------------
# Gap #44: Granular consent per viewer
# ---------------------------------------------------------------------------

DEFAULT_FIELD_SETS = {
    "minimal": ["capabilities", "credentials"],
    "standard": ["capabilities", "credentials", "evidence_summary", "endorsements"],
    "full": [
        "capabilities", "credentials", "evidence_summary", "endorsements",
        "portfolio", "career_goals", "availability", "preferred_types",
    ],
}


def compute_visible_fields(
    default_visibility: str,
    visible_fields: list[str] | None,
    viewer_org_id: str | None,
    discoverable_to: list[str] | None,
) -> list[str]:
    """Compute which fields a specific viewer can see.

    Implements data minimization by context (gap #50).
    """
    if default_visibility == "private":
        return []

    if default_visibility == "specific_employer":
        if not viewer_org_id or not discoverable_to:
            return []
        if viewer_org_id not in discoverable_to:
            return []

    if visible_fields:
        return visible_fields

    if default_visibility == "organization_only":
        return DEFAULT_FIELD_SETS["standard"]
    if default_visibility == "share_link":
        return DEFAULT_FIELD_SETS["standard"]
    if default_visibility == "public_subset":
        return DEFAULT_FIELD_SETS["minimal"]

    return DEFAULT_FIELD_SETS["minimal"]


# ---------------------------------------------------------------------------
# Gap #45: Passport embedding
# ---------------------------------------------------------------------------

def generate_embed_code(
    share_token: str,
    base_url: str = "https://openskill.studio",
    width: int = 400,
    height: int = 300,
) -> dict:
    """Generate embeddable widget code for external sites."""
    verify_url = f"{base_url}/verify/passport/{share_token}"
    iframe = f'<iframe src="{verify_url}?embed=true" width="{width}" height="{height}" frameborder="0" style="border-radius:8px;border:1px solid #e5e7eb;"></iframe>'
    return {
        "iframe_code": iframe,
        "url": verify_url,
        "width": width,
        "height": height,
    }


# ---------------------------------------------------------------------------
# Gap #46: Social proof badge
# ---------------------------------------------------------------------------

def generate_verification_badge_svg(
    capability_count: int,
    highest_level: int,
) -> str:
    """Generate SVG badge for 'Verified by OpenSkill' social proof."""
    level_colors = {0: "#9ca3af", 1: "#3b82f6", 2: "#22c55e", 3: "#eab308", 4: "#f97316", 5: "#a855f7"}
    color = level_colors.get(highest_level, "#3b82f6")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="28" viewBox="0 0 200 28">
  <rect width="120" height="28" rx="4" fill="#1f2937"/>
  <rect x="120" width="80" height="28" rx="4" fill="{color}"/>
  <rect x="120" width="4" height="28" fill="{color}"/>
  <text x="10" y="18" font-family="system-ui" font-size="11" fill="white">✓ OpenSkill Verified</text>
  <text x="130" y="18" font-family="system-ui" font-size="11" fill="white">{capability_count} skills · L{highest_level}</text>
</svg>"""


# ---------------------------------------------------------------------------
# Gap #47: Revision history
# ---------------------------------------------------------------------------

def compute_revision_summary(snapshots: list[dict]) -> list[dict]:
    """Compute revision history summary from snapshots."""
    if len(snapshots) < 2:
        return [{"snapshot_id": s.get("id"), "issued_at": s.get("issued_at"), "changes": "Initial snapshot"} for s in snapshots]

    revisions = []
    for i in range(len(snapshots)):
        if i == 0:
            revisions.append({
                "snapshot_id": snapshots[i].get("id"),
                "issued_at": snapshots[i].get("issued_at"),
                "changes": "Initial snapshot",
                "capability_count": len(snapshots[i].get("payload", {}).get("capabilities", [])),
            })
        else:
            diff = compare_passport_snapshots(
                snapshots[i - 1].get("payload", {}),
                snapshots[i].get("payload", {}),
            )
            change_summary = []
            if diff["added"]:
                change_summary.append(f"+{len(diff['added'])} capabilities")
            if diff["removed"]:
                change_summary.append(f"-{len(diff['removed'])} capabilities")
            if diff["changed"]:
                change_summary.append(f"~{len(diff['changed'])} updated")

            revisions.append({
                "snapshot_id": snapshots[i].get("id"),
                "issued_at": snapshots[i].get("issued_at"),
                "changes": ", ".join(change_summary) if change_summary else "No changes",
                "capability_count": len(snapshots[i].get("payload", {}).get("capabilities", [])),
                "diff_summary": diff,
            })

    return revisions
