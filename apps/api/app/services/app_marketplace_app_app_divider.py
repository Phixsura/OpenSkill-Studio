"""Divider — section divider with optional label."""


def build_divider(*, label: str | None = None, variant: str = "line",
                    spacing: str = "md") -> dict:
    variants = {
        "line": {"class": "border-t", "type": "line"},
        "dashed": {"class": "border-t border-dashed", "type": "dashed"},
        "dotted": {"class": "border-t border-dotted", "type": "dotted"},
        "gradient": {"class": "h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent", "type": "gradient"},
    }
    spacings = {"sm": "my-2", "md": "my-4", "lg": "my-8", "xl": "my-12"}
    v = variants.get(variant, variants["line"])
    s = spacings.get(spacing, spacings["md"])
    return {"label": label, "has_label": label is not None,
            "variant_class": v["class"], "spacing_class": s, "variant": variant}
