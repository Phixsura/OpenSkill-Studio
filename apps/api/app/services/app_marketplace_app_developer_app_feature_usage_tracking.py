"""Feature usage tracking — track which app features are actually used."""

from collections import defaultdict


def track_feature_usage(*, app_id: str, feature: str, user_id: str) -> dict:
    return {"app_id": app_id, "feature": feature, "user_id": user_id, "action": "used"}


def compute_feature_adoption(*, events: list[dict], total_users: int) -> list[dict]:
    by_feature = defaultdict(set)
    for e in events:
        by_feature[e.get("feature", "")].add(e.get("user_id", ""))
    result = []
    for feature, users in sorted(by_feature.items(), key=lambda x: -len(x[1])):
        adoption = round(len(users) / max(total_users, 1) * 100, 1)
        result.append({"feature": feature, "unique_users": len(users), "adoption_pct": adoption})
    return result


def identify_unused_features(*, all_features: list[str], used_features: list[str]) -> list[str]:
    return sorted(set(all_features) - set(used_features))


def compute_feature_stickiness(*, daily_users: dict[str, int], monthly_users: dict[str, int]) -> dict:
    result = {}
    for feature in set(list(daily_users.keys()) + list(monthly_users.keys())):
        dau = daily_users.get(feature, 0)
        mau = monthly_users.get(feature, 0)
        result[feature] = {"dau": dau, "mau": mau,
                            "stickiness": round(dau / max(mau, 1) * 100, 1)}
    return result
