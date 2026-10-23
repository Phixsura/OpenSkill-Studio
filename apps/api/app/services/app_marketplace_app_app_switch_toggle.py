"""Switch toggle — boolean toggle switch configurations."""


def build_toggle(*, label: str, description: str | None = None, enabled: bool = False,
                   size: str = "md", disabled: bool = False) -> dict:
    sizes = {"sm": {"width": 36, "height": 20}, "md": {"width": 44, "height": 24},
             "lg": {"width": 52, "height": 28}}
    s = sizes.get(size, sizes["md"])
    return {
        "label": label,
        "description": description,
        "enabled": enabled,
        "size": size,
        "dimensions": s,
        "disabled": disabled,
        "aria_label": f"Toggle {label}",
    }
