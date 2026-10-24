"""Radio group — single-select radio button group."""


def build_radio_group(*, name: str, label: str, options: list[dict],
                        selected: str | None = None) -> dict:
    items = [{"value": o["value"], "label": o.get("label", o["value"]),
              "description": o.get("description"), "icon": o.get("icon"),
              "selected": o["value"] == selected} for o in options]
    return {"name": name, "label": label, "items": items,
            "selected": selected, "has_selection": selected is not None}
