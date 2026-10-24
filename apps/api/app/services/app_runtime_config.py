"""App runtime config — configuration for sandbox execution runtime."""

SUPPORTED_RUNTIMES = {
    "python3.11": {"image": "python:3.11-slim", "entrypoint": "python", "ext": ".py"},
    "python3.12": {"image": "python:3.12-slim", "entrypoint": "python", "ext": ".py"},
    "nodejs20": {"image": "node:20-slim", "entrypoint": "node", "ext": ".js"},
    "nodejs22": {"image": "node:22-slim", "entrypoint": "node", "ext": ".js"},
}

def get_runtime_config(runtime: str) -> dict | None:
    return SUPPORTED_RUNTIMES.get(runtime)

def list_runtimes() -> list[str]:
    return sorted(SUPPORTED_RUNTIMES.keys())

def is_supported_runtime(runtime: str) -> bool:
    return runtime in SUPPORTED_RUNTIMES
