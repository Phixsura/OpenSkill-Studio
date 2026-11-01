"""Developer quicklinks — personalized shortcuts based on developer activity."""

def get_quicklinks(*, developer: dict, apps: list[dict]) -> list[dict]:
    links = [{"label": "Create New App", "url": "/developer/apps/new", "icon": "➕", "priority": 1}]
    if apps:
        latest = apps[0]
        links.append({"label": f"Edit {latest['name']}", "url": f"/developer/apps/{latest.get('id')}", "icon": "✏️", "priority": 2})
    if developer.get("verified"):
        links.append({"label": "Analytics Dashboard", "url": "/developer/analytics", "icon": "📊", "priority": 3})
    links.append({"label": "API Documentation", "url": "/developer/docs", "icon": "📚", "priority": 4})
    links.append({"label": "Community Forum", "url": "/community", "icon": "💬", "priority": 5})
    return sorted(links, key=lambda l: l["priority"])
