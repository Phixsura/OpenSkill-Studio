"""Summary card — compact summary card with key metrics."""


def build_summary_card(*, title: str, metrics: list[dict], status: str = "ok",
                          icon: str = "📊", link: str | None = None) -> dict:
    formatted = []
    for m in metrics:
        val = m["value"]
        if m.get("format") == "currency":
            display = f"${val:,.2f}"
        elif m.get("format") == "pct":
            display = f"{val}%"
        elif m.get("format") == "compact" and val >= 1000:
            display = f"{val / 1000:.1f}K"
        else:
            display = f"{val:,}" if isinstance(val, int) else str(val)
        formatted.append({"label": m["label"], "value": val, "display": display})
    return {"title": title, "icon": icon, "metrics": formatted,
            "status": status, "link": link, "metric_count": len(formatted)}
