"""Log aggregator — aggregate logs from multiple sources."""

from datetime import datetime


def aggregate_logs(*, sources: list[dict]) -> dict:
    all_logs = []
    source_stats: dict[str, int] = {}
    level_stats: dict[str, int] = {}
    for src in sources:
        name = src["name"]
        logs = src.get("logs", [])
        source_stats[name] = len(logs)
        for log in logs:
            log["source"] = name
            lvl = log.get("level", "info")
            level_stats[lvl] = level_stats.get(lvl, 0) + 1
            all_logs.append(log)
    all_logs.sort(key=lambda l: l.get("timestamp", ""), reverse=True)
    return {
        "logs": all_logs[:200],
        "total_logs": len(all_logs),
        "by_source": source_stats,
        "by_level": level_stats,
        "source_count": len(sources),
        "has_errors": level_stats.get("error", 0) + level_stats.get("critical", 0) > 0,
    }
