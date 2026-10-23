"""App modal — reusable modal dialog configuration."""

import html

MODAL_SIZES = {"sm": "max-w-sm", "md": "max-w-md", "lg": "max-w-lg", "xl": "max-w-xl", "full": "max-w-4xl"}


def build_modal_config(*, title: str, size: str = "md", closable: bool = True,
                         has_footer: bool = True, danger: bool = False) -> dict:
    return {
        "title": html.escape(title),
        "size": size,
        "size_class": MODAL_SIZES.get(size, MODAL_SIZES["md"]),
        "closable": closable,
        "has_footer": has_footer,
        "danger": danger,
        "overlay": True,
    }
