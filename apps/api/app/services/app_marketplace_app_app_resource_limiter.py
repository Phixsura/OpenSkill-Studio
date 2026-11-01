"""Resource limiter — container resource limits and requests config."""


PRESETS = {
    "micro": {"cpu_m": 100, "memory_mb": 128, "replicas": 1},
    "small": {"cpu_m": 250, "memory_mb": 256, "replicas": 1},
    "medium": {"cpu_m": 500, "memory_mb": 512, "replicas": 2},
    "large": {"cpu_m": 1000, "memory_mb": 1024, "replicas": 3},
    "xlarge": {"cpu_m": 2000, "memory_mb": 2048, "replicas": 5},
}


def build_resource_config(*, preset: str | None = None, cpu_m: int | None = None,
                            memory_mb: int | None = None, replicas: int = 1) -> dict:
    if preset and preset in PRESETS:
        base = dict(PRESETS[preset])
    else:
        base = {"cpu_m": cpu_m or 250, "memory_mb": memory_mb or 256, "replicas": replicas}
    monthly_cost = round((base["cpu_m"] / 1000 * 15 + base["memory_mb"] / 1024 * 5) * base["replicas"], 2)
    return {**base, "preset": preset, "monthly_cost_usd": monthly_cost,
            "cpu_display": f"{base['cpu_m']}m" if base["cpu_m"] < 1000 else f"{base['cpu_m']/1000:.1f} cores",
            "memory_display": f"{base['memory_mb']}MB" if base["memory_mb"] < 1024 else f"{base['memory_mb']/1024:.1f}GB"}


def list_presets() -> list[dict]:
    return [{"id": k, **v, "monthly_cost_usd": round((v["cpu_m"]/1000*15 + v["memory_mb"]/1024*5)*v["replicas"], 2)}
            for k, v in PRESETS.items()]
