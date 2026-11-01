"""Loading state — configurable loading indicators."""


LOADING_VARIANTS = {
    "spinner": {"type": "spinner", "label": "Loading..."},
    "dots": {"type": "dots", "label": "Loading..."},
    "skeleton": {"type": "skeleton", "label": None},
    "progress": {"type": "progress", "label": "Loading..."},
    "pulse": {"type": "pulse", "label": None},
}


def get_loading_state(*, variant: str = "spinner", message: str | None = None,
                        progress_pct: int | None = None) -> dict:
    config = LOADING_VARIANTS.get(variant, LOADING_VARIANTS["spinner"])
    return {
        "variant": variant,
        "type": config["type"],
        "message": message or config["label"],
        "progress_pct": progress_pct,
        "show_progress": progress_pct is not None,
        "accessible_label": message or "Loading content",
    }
