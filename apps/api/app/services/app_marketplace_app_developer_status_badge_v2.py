"""Developer status badge v2 — dynamic SVG badges for README embedding."""


def generate_badge_url(*, app_slug: str, metric: str, value: str, color: str = "blue") -> str:
    return f"https://img.openskill.dev/badge/{app_slug}/{metric}-{value}-{color}.svg"


def compute_badge_data(*, app: dict) -> list[dict]:
    badges = []
    status = app.get("status", "draft")
    badges.append({"metric": "status", "value": status,
                    "color": "green" if status == "published" else "yellow" if status == "in_review" else "gray"})
    installs = app.get("install_count", 0)
    badges.append({"metric": "installs", "value": f"{installs:,}",
                    "color": "blue" if installs > 100 else "lightblue"})
    rating = app.get("avg_rating", 0)
    if rating > 0:
        badges.append({"metric": "rating", "value": f"{rating:.1f}★",
                        "color": "green" if rating >= 4 else "yellow" if rating >= 3 else "red"})
    return badges


def generate_markdown_badges(*, app_slug: str, badges: list[dict]) -> str:
    lines = []
    for b in badges:
        url = generate_badge_url(app_slug=app_slug, metric=b["metric"], value=b["value"], color=b["color"])
        lines.append(f"![{b['metric']}]({url})")
    return " ".join(lines)
