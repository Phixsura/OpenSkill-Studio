"""Publishing page builder — compile publish flow page data."""

def build_publishing_page(*, app: dict, can_publish: bool, errors: list[str], warnings: list[str]) -> dict:
    return {"app_name": app.get("name"), "can_publish": can_publish, "errors": errors, "warnings": warnings,
            "steps_remaining": len(errors), "ready": can_publish and len(errors) == 0}
