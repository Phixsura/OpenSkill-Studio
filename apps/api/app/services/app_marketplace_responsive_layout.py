"""Responsive layout — build adaptive layouts for different screen sizes."""

BREAKPOINTS = {"mobile": 640, "tablet": 768, "desktop": 1024, "wide": 1280}


def get_layout_config(*, page_type: str, screen_width: int) -> dict:
    device = "mobile" if screen_width < 640 else "tablet" if screen_width < 1024 else "desktop"
    layouts = {
        "marketplace_home": {
            "mobile": {"columns": 1, "show_sidebar": False, "hero_height": "200px", "card_size": "full"},
            "tablet": {"columns": 2, "show_sidebar": False, "hero_height": "300px", "card_size": "medium"},
            "desktop": {"columns": 4, "show_sidebar": True, "hero_height": "400px", "card_size": "small"},
        },
        "app_detail": {
            "mobile": {"columns": 1, "show_sidebar": False, "layout": "stacked"},
            "tablet": {"columns": 1, "show_sidebar": True, "layout": "sidebar_right"},
            "desktop": {"columns": 1, "show_sidebar": True, "layout": "sidebar_right"},
        },
        "developer_dashboard": {
            "mobile": {"columns": 1, "show_sidebar": False, "compact_stats": True},
            "tablet": {"columns": 2, "show_sidebar": True, "compact_stats": False},
            "desktop": {"columns": 3, "show_sidebar": True, "compact_stats": False},
        },
    }
    page_layouts = layouts.get(page_type, layouts["marketplace_home"])
    return {"device": device, "screen_width": screen_width, **page_layouts.get(device, page_layouts["desktop"])}


def should_lazy_load(*, position: int, viewport_items: int) -> bool:
    return position >= viewport_items


def get_image_sizes(*, device: str) -> dict:
    sizes = {
        "mobile": {"app_icon": 48, "screenshot": 320, "avatar": 32, "hero": 640},
        "tablet": {"app_icon": 56, "screenshot": 480, "avatar": 40, "hero": 768},
        "desktop": {"app_icon": 64, "screenshot": 640, "avatar": 48, "hero": 1280},
    }
    return sizes.get(device, sizes["desktop"])
