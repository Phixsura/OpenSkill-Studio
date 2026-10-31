"""Modal manager — manage modal dialog stack and configurations."""


MODAL_SIZES = {"sm": "max-w-sm", "md": "max-w-md", "lg": "max-w-lg", "xl": "max-w-xl", "full": "max-w-4xl"}


def create_modal(*, modal_id: str, title: str, size: str = "md",
                   dismissible: bool = True, has_footer: bool = True) -> dict:
    if size not in MODAL_SIZES:
        return {"error": f"Invalid size. Valid: {', '.join(sorted(MODAL_SIZES))}"}
    return {
        "modal_id": modal_id,
        "title": title,
        "size": size,
        "size_class": MODAL_SIZES[size],
        "dismissible": dismissible,
        "has_footer": has_footer,
    }


def manage_modal_stack(*, stack: list[str], action: str, modal_id: str | None = None) -> dict:
    if action == "push" and modal_id:
        return {"stack": stack + [modal_id], "active": modal_id, "depth": len(stack) + 1}
    elif action == "pop" and stack:
        new_stack = stack[:-1]
        return {"stack": new_stack, "active": new_stack[-1] if new_stack else None, "depth": len(new_stack)}
    elif action == "clear":
        return {"stack": [], "active": None, "depth": 0}
    return {"stack": stack, "active": stack[-1] if stack else None, "depth": len(stack)}
