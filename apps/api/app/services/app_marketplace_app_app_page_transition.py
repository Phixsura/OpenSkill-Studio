"""Page transition — animation configs for page transitions."""


TRANSITIONS = {
    "fade": {"enter": "opacity-0 → opacity-100", "exit": "opacity-100 → opacity-0", "duration_ms": 200},
    "slide_left": {"enter": "translateX(100%) → translateX(0)", "exit": "translateX(0) → translateX(-100%)", "duration_ms": 300},
    "slide_up": {"enter": "translateY(100%) → translateY(0)", "exit": "translateY(0) → translateY(-100%)", "duration_ms": 300},
    "scale": {"enter": "scale(0.95) → scale(1)", "exit": "scale(1) → scale(0.95)", "duration_ms": 200},
    "none": {"enter": "none", "exit": "none", "duration_ms": 0},
}


def get_transition(*, name: str = "fade") -> dict:
    t = TRANSITIONS.get(name, TRANSITIONS["fade"])
    return {"name": name, **t, "easing": "ease-in-out"}


def get_all_transitions() -> dict:
    return {"transitions": [{"name": k, **v} for k, v in TRANSITIONS.items()],
            "total": len(TRANSITIONS), "default": "fade"}
