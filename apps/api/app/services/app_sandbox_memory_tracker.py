"""Sandbox memory tracker — track peak memory usage across executions."""

from collections import defaultdict

_memory_peaks: dict[str, list[float]] = defaultdict(list)


def record_memory(app_id: str, peak_mb: float) -> None:
    _memory_peaks[app_id].append(peak_mb)
    if len(_memory_peaks[app_id]) > 1000:
        _memory_peaks[app_id] = _memory_peaks[app_id][-500:]


def get_memory_stats(app_id: str) -> dict:
    peaks = _memory_peaks.get(app_id, [])
    if not peaks:
        return {"count": 0, "avg_mb": 0, "max_mb": 0, "p95_mb": 0}
    sorted_peaks = sorted(peaks)
    n = len(sorted_peaks)
    return {
        "count": n,
        "avg_mb": round(sum(peaks) / n, 1),
        "max_mb": round(max(peaks), 1),
        "p95_mb": round(sorted_peaks[int(n * 0.95)], 1),
    }


def is_memory_warning(app_id: str, limit_mb: float) -> bool:
    stats = get_memory_stats(app_id)
    return stats["p95_mb"] > limit_mb * 0.8
