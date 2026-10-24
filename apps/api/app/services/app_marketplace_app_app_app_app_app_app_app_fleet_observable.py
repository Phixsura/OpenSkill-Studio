"""Fleet Observable — track data visualization notebooks."""
from __future__ import annotations
def fleet_observable_status(notebooks: list[dict]) -> dict:
    published = [n for n in notebooks if n.get("published", True)]
    cells = sum(n.get("cells", 0) for n in notebooks)
    views_24h = sum(n.get("views_24h", 0) for n in notebooks)
    return {"notebooks": len(notebooks), "published": len(published), "cells": cells,
            "views_24h": views_24h, "all_published": len(published) == len(notebooks)}
