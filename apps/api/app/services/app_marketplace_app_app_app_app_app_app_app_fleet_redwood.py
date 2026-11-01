"""Fleet RedwoodJS — track full-stack JS framework."""
from __future__ import annotations
def fleet_redwood_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    cells = sum(a.get("cells", 0) for a in apps)
    services = sum(a.get("services", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "cells": cells,
            "services": services, "all_deployed": len(deployed) == len(apps)}
