"""Modal manager — manage modal stack with size and focus control."""
from __future__ import annotations

MODAL_SIZES = {
    "sm": {"width": "400px", "max_height": "50vh"},
    "md": {"width": "560px", "max_height": "70vh"},
    "lg": {"width": "720px", "max_height": "80vh"},
    "xl": {"width": "960px", "max_height": "90vh"},
    "full": {"width": "100vw", "max_height": "100vh"},
}


def create_modal(*, title: str, size: str = "md", closable: bool = True,
                   has_footer: bool = True) -> dict:
    dims = MODAL_SIZES.get(size, MODAL_SIZES["md"])
    return {"title": title, "size": size, **dims,
            "closable": closable, "has_footer": has_footer, "open": True}


def manage_stack(modals: list[dict]) -> dict:
    return {"stack": modals, "depth": len(modals),
            "top": modals[-1] if modals else None,
            "has_overlay": len(modals) > 0}
