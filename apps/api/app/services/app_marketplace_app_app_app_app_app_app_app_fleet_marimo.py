"""Fleet Marimo — track reactive Python notebook."""
from __future__ import annotations
def fleet_marimo_status(notebooks: list[dict]) -> dict:
    running = [n for n in notebooks if n.get("running", True)]
    cells = sum(n.get("cells", 0) for n in notebooks)
    users_24h = sum(n.get("users_24h", 0) for n in notebooks)
    return {"notebooks": len(notebooks), "running": len(running), "cells": cells,
            "users_24h": users_24h, "all_running": len(running) == len(notebooks)}
