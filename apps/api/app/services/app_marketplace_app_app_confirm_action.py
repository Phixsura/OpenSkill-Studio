"""Confirm action — wrap dangerous operations with confirmation."""


def require_confirmation(*, action: str, resource_name: str, danger_level: str = "medium") -> dict:
    configs = {
        "low": {"require_typing": False, "countdown_sec": 0, "message": f"Are you sure you want to {action} {resource_name}?"},
        "medium": {"require_typing": False, "countdown_sec": 3, "message": f"This will {action} {resource_name}. This may cause disruption."},
        "high": {"require_typing": True, "countdown_sec": 5, "message": f"This will permanently {action} {resource_name}. This action CANNOT be undone."},
    }
    config = configs.get(danger_level, configs["medium"])
    return {
        "action": action,
        "resource_name": resource_name,
        "danger_level": danger_level,
        **config,
        "confirm_word": resource_name.upper() if config["require_typing"] else None,
    }
