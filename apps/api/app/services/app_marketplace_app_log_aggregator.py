"""Log aggregator — combine logs from multiple sources with dedup."""

from collections import defaultdict


def aggregate_logs(*, sources: dict[str, list[dict]], dedup: bool = True) -> dict:
    all_logs = []
    for source, logs in sources.items():
        for log in logs:
            all_logs.append({**log, "source": source})
    all_logs.sort(key=lambda l: l.get("timestamp", ""), reverse=True)
    if dedup:
        seen = set()
        deduped = []
        for log in all_logs:
            key = f"{log.get('timestamp')}:{log.get('message', '')}"
            if key not in seen:
                seen.add(key)
                deduped.append(log)
        all_logs = deduped
    return {"logs": all_logs, "total": len(all_logs), "sources": list(sources.keys())}


def compute_log_volume(*, logs: list[dict]) -> dict:
    by_level = defaultdict(int)
    by_source = defaultdict(int)
    for l in logs:
        by_level[l.get("level", "unknown")] += 1
        by_source[l.get("source", "unknown")] += 1
    return {"by_level": dict(by_level), "by_source": dict(by_source), "total": len(logs)}
