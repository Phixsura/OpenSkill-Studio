"""Hero section — configurable hero banner for app pages."""

import html


def build_hero(*, headline: str, subheadline: str, cta_primary: str,
                 cta_secondary: str | None = None, stats: list[dict] | None = None,
                 gradient: str = "from-blue-600 to-purple-600") -> dict:
    return {
        "headline": html.escape(headline),
        "subheadline": html.escape(subheadline),
        "cta_primary": cta_primary,
        "cta_secondary": cta_secondary,
        "stats": stats or [],
        "gradient": gradient,
        "has_stats": bool(stats),
        "has_secondary_cta": cta_secondary is not None,
    }
