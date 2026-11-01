"""Search bar — configurable search bar with history and suggestions."""


def build_search_bar_config(*, placeholder: str = "Search...", show_history: bool = True,
                               max_history: int = 5, shortcut: str = "Cmd+K") -> dict:
    return {
        "placeholder": placeholder,
        "show_history": show_history,
        "max_history": max_history,
        "shortcut": shortcut,
        "autocomplete": True,
        "min_query_length": 2,
        "debounce_ms": 300,
    }


def filter_search_history(*, history: list[str], current_query: str, limit: int = 5) -> dict:
    q = current_query.lower()
    if not q:
        return {"suggestions": history[:limit], "from_history": True}
    matched = [h for h in history if q in h.lower()]
    return {"suggestions": matched[:limit], "from_history": True, "query": current_query}
