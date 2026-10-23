"""Loading states manager — configure loading indicators per context."""
from __future__ import annotations

LOADING_CONFIGS = {
    "page": {"type": "skeleton", "delay_ms": 200, "min_duration_ms": 500},
    "button": {"type": "spinner", "delay_ms": 0, "min_duration_ms": 300},
    "table": {"type": "skeleton", "delay_ms": 100, "min_duration_ms": 400},
    "modal": {"type": "spinner", "delay_ms": 0, "min_duration_ms": 200},
    "inline": {"type": "dots", "delay_ms": 0, "min_duration_ms": 100},
    "global": {"type": "progress_bar", "delay_ms": 300, "min_duration_ms": 800},
}


def get_loading_config(context: str) -> dict:
    config = LOADING_CONFIGS.get(context, LOADING_CONFIGS["page"])
    return {"context": context, **config}


def should_show_loader(*, elapsed_ms: int, context: str) -> bool:
    config = LOADING_CONFIGS.get(context, LOADING_CONFIGS["page"])
    return elapsed_ms >= config["delay_ms"]


def list_contexts() -> list[dict]:
    return [{"context": k, **v} for k, v in LOADING_CONFIGS.items()]
