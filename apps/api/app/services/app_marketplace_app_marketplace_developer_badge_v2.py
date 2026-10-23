"""Developer badge v2 — SVG badge generation for README embedding."""


def generate_installs_badge(*, count: int, app_slug: str) -> dict:
    color = "brightgreen" if count >= 1000 else "blue" if count >= 100 else "lightgrey"
    label = f"{count:,}" if count < 10000 else f"{count // 1000}k+"
    return {"type": "installs", "label": label, "color": color,
            "url": f"https://img.openskill.dev/badge/{app_slug}/installs-{label}-{color}.svg",
            "markdown": f"![installs](https://img.openskill.dev/badge/{app_slug}/installs-{label}-{color}.svg)"}


def generate_rating_badge(*, rating: float, app_slug: str) -> dict:
    color = "brightgreen" if rating >= 4.5 else "green" if rating >= 4 else "yellow" if rating >= 3 else "red"
    label = f"{rating:.1f}★"
    return {"type": "rating", "label": label, "color": color,
            "url": f"https://img.openskill.dev/badge/{app_slug}/rating-{label}-{color}.svg",
            "markdown": f"![rating](https://img.openskill.dev/badge/{app_slug}/rating-{label}-{color}.svg)"}


def generate_status_badge(*, status: str, app_slug: str) -> dict:
    colors = {"published": "brightgreen", "in_review": "yellow", "draft": "lightgrey", "suspended": "red"}
    color = colors.get(status, "lightgrey")
    return {"type": "status", "label": status, "color": color,
            "url": f"https://img.openskill.dev/badge/{app_slug}/status-{status}-{color}.svg"}


def generate_all_badges(*, app: dict) -> list[dict]:
    slug = app.get("slug", app.get("id", ""))
    badges = [generate_status_badge(status=app.get("status", "draft"), app_slug=slug)]
    if app.get("install_count", 0) > 0:
        badges.append(generate_installs_badge(count=app["install_count"], app_slug=slug))
    if app.get("avg_rating", 0) > 0:
        badges.append(generate_rating_badge(rating=app["avg_rating"], app_slug=slug))
    return badges
