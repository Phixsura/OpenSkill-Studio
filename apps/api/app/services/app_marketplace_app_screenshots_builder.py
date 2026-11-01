"""Screenshots builder — compile app screenshots for detail page."""

def build_screenshots(screenshots: list[dict]) -> dict:
    return {"screenshots": screenshots, "count": len(screenshots), "has_screenshots": len(screenshots) > 0}
