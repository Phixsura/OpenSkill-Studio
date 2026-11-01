"""Animation config — motion preferences and transition settings."""

ANIMATIONS = {
    "page_transition": {"duration_ms": 300, "easing": "ease-in-out", "type": "fade"},
    "modal_open": {"duration_ms": 200, "easing": "ease-out", "type": "scale-fade"},
    "modal_close": {"duration_ms": 150, "easing": "ease-in", "type": "fade"},
    "toast_enter": {"duration_ms": 300, "easing": "ease-out", "type": "slide-up"},
    "toast_exit": {"duration_ms": 200, "easing": "ease-in", "type": "slide-down"},
    "skeleton_pulse": {"duration_ms": 1500, "easing": "ease-in-out", "type": "pulse"},
    "hover_scale": {"duration_ms": 150, "easing": "ease-out", "type": "scale", "scale": 1.02},
    "dropdown_open": {"duration_ms": 150, "easing": "ease-out", "type": "slide-down"},
}


def get_animation(*, name: str) -> dict | None:
    return ANIMATIONS.get(name)


def get_reduced_motion_config() -> dict:
    return {k: {**v, "duration_ms": 0} for k, v in ANIMATIONS.items()}


def should_animate(*, prefers_reduced_motion: bool) -> bool:
    return not prefers_reduced_motion
