"""Text input — configurable text input field."""


INPUT_TYPES = {"text", "email", "password", "url", "number", "tel", "search"}


def build_input_config(*, name: str, label: str, input_type: str = "text",
                         placeholder: str = "", required: bool = False,
                         min_length: int | None = None, max_length: int | None = None,
                         pattern: str | None = None, help_text: str | None = None) -> dict:
    if input_type not in INPUT_TYPES:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(INPUT_TYPES))}"}
    return {
        "name": name, "label": label, "type": input_type,
        "placeholder": placeholder, "required": required,
        "min_length": min_length, "max_length": max_length,
        "pattern": pattern, "help_text": help_text,
        "aria_label": label,
    }
