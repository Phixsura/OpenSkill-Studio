"""Tag cloud — generate weighted tag clouds from app metadata."""

from collections import Counter


def build_tag_cloud(*, apps: list[dict], max_tags: int = 30) -> dict:
    tag_counter: Counter = Counter()
    for app in apps:
        for tag in app.get("tags", []):
            tag_counter[tag.lower()] += 1
    top_tags = tag_counter.most_common(max_tags)
    if not top_tags:
        return {"tags": [], "total_unique": 0}
    max_count = top_tags[0][1]
    tags = [{"tag": tag, "count": count,
             "weight": round(count / max_count * 100),
             "size": max(12, min(36, int(count / max_count * 36)))}
            for tag, count in top_tags]
    return {"tags": tags, "total_unique": len(tag_counter), "displayed": len(tags)}
