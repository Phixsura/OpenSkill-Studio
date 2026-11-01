"""Developer quota usage — track resource usage against quotas."""


def compute_quota_usage(*, apps: int, max_apps: int, versions: int, max_versions: int,
                         keys: int, max_keys: int, secrets: int, max_secrets: int) -> dict:
    items = [
        {"resource": "apps", "used": apps, "limit": max_apps},
        {"resource": "versions", "used": versions, "limit": max_versions},
        {"resource": "api_keys", "used": keys, "limit": max_keys},
        {"resource": "secrets", "used": secrets, "limit": max_secrets},
    ]
    for item in items:
        item["pct"] = round(item["used"] / item["limit"] * 100, 1) if item["limit"] > 0 else 0
        item["warning"] = item["pct"] >= 80
        item["exceeded"] = item["used"] >= item["limit"]
    return {"items": items, "any_exceeded": any(i["exceeded"] for i in items),
            "any_warning": any(i["warning"] for i in items)}
