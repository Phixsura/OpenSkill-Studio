"""User segment targeting — target features and content to user segments."""


SEGMENT_RULES = {
    "new_users": lambda u: u.get("days_since_signup", 0) <= 7,
    "power_users": lambda u: u.get("actions_30d", 0) >= 100,
    "paying": lambda u: u.get("plan", "free") != "free",
    "churning": lambda u: u.get("days_inactive", 0) >= 14,
    "developers": lambda u: u.get("is_developer", False),
    "enterprise": lambda u: u.get("plan") == "enterprise",
}


def match_segments(*, user: dict) -> dict:
    matched = []
    for seg_id, rule in SEGMENT_RULES.items():
        if rule(user):
            matched.append(seg_id)
    return {"user_id": user.get("id", ""), "segments": matched,
            "segment_count": len(matched)}


def target_content(*, content_rules: list[dict], user_segments: list[str]) -> dict:
    matched_content = []
    segment_set = set(user_segments)
    for rule in content_rules:
        target = set(rule.get("target_segments", []))
        exclude = set(rule.get("exclude_segments", []))
        if target & segment_set and not (exclude & segment_set):
            matched_content.append(rule.get("content_id"))
    return {"matched_content": matched_content, "total_matched": len(matched_content)}
