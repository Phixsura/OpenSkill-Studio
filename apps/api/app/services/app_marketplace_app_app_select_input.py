"""Select input — configurable dropdown select field."""


def build_select_config(*, name: str, label: str, options: list[dict],
                          placeholder: str = "Select...", required: bool = False,
                          multiple: bool = False) -> dict:
    return {
        "name": name, "label": label,
        "options": [{"value": o.get("value", ""), "label": o.get("label", o.get("value", "")),
                      "icon": o.get("icon"), "disabled": o.get("disabled", False)} for o in options],
        "placeholder": placeholder, "required": required, "multiple": multiple,
        "option_count": len(options),
    }
