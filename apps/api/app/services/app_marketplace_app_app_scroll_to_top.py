"""Scroll to top — scroll behavior configuration."""


def get_scroll_config(*, show_threshold: int = 300, smooth: bool = True,
                        position: str = "bottom-right") -> dict:
    positions = {
        "bottom-right": "fixed bottom-6 right-6",
        "bottom-left": "fixed bottom-6 left-6",
        "bottom-center": "fixed bottom-6 left-1/2 -translate-x-1/2",
    }
    return {
        "show_threshold": show_threshold,
        "smooth": smooth,
        "scroll_behavior": "smooth" if smooth else "auto",
        "position": position,
        "position_class": positions.get(position, positions["bottom-right"]),
    }
