"""404 suggestions — smart suggestions for not-found pages."""

import html
from difflib import get_close_matches


def suggest_pages(*, requested_path: str, available_paths: list[str],
                    max_suggestions: int = 5) -> dict:
    path = requested_path.strip("/").lower()
    matches = get_close_matches(path, [p.strip("/").lower() for p in available_paths],
                                  n=max_suggestions, cutoff=0.4)
    original_map = {p.strip("/").lower(): p for p in available_paths}
    suggestions = [original_map.get(m, m) for m in matches]
    segments = path.split("/")
    category = segments[0] if segments else None
    category_matches = [p for p in available_paths if p.strip("/").lower().startswith(f"{category}/")][:3] if category else []
    return {"requested": html.escape(requested_path),
            "suggestions": suggestions,
            "category_matches": category_matches,
            "has_suggestions": len(suggestions) > 0}
