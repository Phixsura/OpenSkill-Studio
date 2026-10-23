"""Responsive grid — generate responsive grid layout configurations."""


BREAKPOINTS = {"sm": 640, "md": 768, "lg": 1024, "xl": 1280}


def build_grid_config(*, items_count: int, min_card_width: int = 280,
                        gap: int = 16) -> dict:
    layouts = {}
    for bp_name, bp_width in BREAKPOINTS.items():
        cols = max(1, (bp_width + gap) // (min_card_width + gap))
        layouts[bp_name] = {"columns": cols, "width": bp_width}
    # Mobile default
    layouts["default"] = {"columns": 1, "width": 0}
    grid_class = f"grid gap-{gap // 4} grid-cols-1 sm:grid-cols-{layouts['sm']['columns']} md:grid-cols-{layouts['md']['columns']} lg:grid-cols-{layouts['lg']['columns']}"
    return {
        "layouts": layouts,
        "grid_class": grid_class,
        "items_count": items_count,
        "gap_px": gap,
        "min_card_width": min_card_width,
    }
