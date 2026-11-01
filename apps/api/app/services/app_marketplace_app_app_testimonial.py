"""Testimonial — collect and display developer testimonials."""

import html


def build_testimonials(*, testimonials: list[dict]) -> dict:
    enriched = []
    for t in testimonials:
        enriched.append({
            "quote": html.escape(t.get("quote", "")),
            "author": html.escape(t.get("author", "")),
            "role": html.escape(t.get("role", "")),
            "company": html.escape(t.get("company", "")),
            "rating": t.get("rating", 5),
            "avatar_initials": "".join(w[0].upper() for w in t.get("author", "?").split()[:2]),
        })
    avg_rating = round(sum(t["rating"] for t in enriched) / max(len(enriched), 1), 1)
    return {"testimonials": enriched, "total": len(enriched), "avg_rating": avg_rating}
