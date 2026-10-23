"""App listing SEO — optimize app listings for search engines."""

import html
import re


def analyze_seo(*, title: str, description: str, category: str,
                  tags: list[str]) -> dict:
    issues = []
    score = 100
    if len(title) < 10:
        issues.append({"field": "title", "issue": "Too short (min 10 chars)", "impact": -15})
        score -= 15
    elif len(title) > 60:
        issues.append({"field": "title", "issue": "Too long (max 60 chars)", "impact": -10})
        score -= 10
    if len(description) < 100:
        issues.append({"field": "description", "issue": "Too short (min 100 chars)", "impact": -20})
        score -= 20
    elif len(description) > 500:
        issues.append({"field": "description", "issue": "Consider shortening (500 char ideal)", "impact": -5})
        score -= 5
    if len(tags) < 3:
        issues.append({"field": "tags", "issue": f"Add more tags ({len(tags)}/3 minimum)", "impact": -10})
        score -= 10
    if not category:
        issues.append({"field": "category", "issue": "Category not set", "impact": -15})
        score -= 15
    return {
        "score": max(score, 0),
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "F",
        "issues": issues,
        "issue_count": len(issues),
    }


def generate_meta_tags(*, title: str, description: str, image_url: str | None = None,
                         url: str = "") -> dict:
    safe_title = html.escape(title[:60])
    safe_desc = html.escape(description[:160])
    tags = {
        "title": safe_title,
        "meta_description": safe_desc,
        "og:title": safe_title,
        "og:description": safe_desc,
        "og:type": "website",
        "og:url": html.escape(url),
    }
    if image_url:
        tags["og:image"] = html.escape(image_url)
    return {"tags": tags, "char_count": {"title": len(title), "description": len(description)}}
