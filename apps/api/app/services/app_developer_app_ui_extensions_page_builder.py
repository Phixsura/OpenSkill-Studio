"""UI extensions page builder — compile UI extensions data."""

def build_extensions_page(*, extensions: list[dict], surfaces_available: list[str]) -> dict:
    used_surfaces = {e.get("surface") for e in extensions}
    return {"extensions": extensions, "count": len(extensions),
            "surfaces_used": sorted(used_surfaces), "surfaces_available": surfaces_available,
            "unused_surfaces": sorted(set(surfaces_available) - used_surfaces)}
