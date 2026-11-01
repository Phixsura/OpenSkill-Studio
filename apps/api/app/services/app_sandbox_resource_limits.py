"""Sandbox resource limits — enforce and validate execution resource limits."""

from dataclasses import dataclass

@dataclass
class ResourceLimits:
    memory_mb: int = 128
    timeout_seconds: int = 30
    cpu_shares: int = 256
    max_output_bytes: int = 1_048_576  # 1MB
    max_log_lines: int = 1000

TIER_LIMITS = {
    "free": ResourceLimits(memory_mb=64, timeout_seconds=10, cpu_shares=128),
    "standard": ResourceLimits(),
    "premium": ResourceLimits(memory_mb=512, timeout_seconds=120, cpu_shares=512),
    "enterprise": ResourceLimits(memory_mb=2048, timeout_seconds=300, cpu_shares=1024, max_output_bytes=10_485_760),
}

MAX_LIMITS = ResourceLimits(memory_mb=4096, timeout_seconds=600, cpu_shares=2048, max_output_bytes=52_428_800)

def get_limits(tier: str = "standard") -> ResourceLimits:
    return TIER_LIMITS.get(tier, TIER_LIMITS["standard"])

def validate_limits(requested: ResourceLimits) -> list[str]:
    errors = []
    if requested.memory_mb > MAX_LIMITS.memory_mb:
        errors.append(f"Memory exceeds max ({MAX_LIMITS.memory_mb}MB)")
    if requested.timeout_seconds > MAX_LIMITS.timeout_seconds:
        errors.append(f"Timeout exceeds max ({MAX_LIMITS.timeout_seconds}s)")
    if requested.memory_mb <= 0:
        errors.append("Memory must be positive")
    if requested.timeout_seconds <= 0:
        errors.append("Timeout must be positive")
    return errors

def clamp_limits(requested: ResourceLimits, tier: str = "standard") -> ResourceLimits:
    tier_max = get_limits(tier)
    return ResourceLimits(
        memory_mb=min(requested.memory_mb, tier_max.memory_mb),
        timeout_seconds=min(requested.timeout_seconds, tier_max.timeout_seconds),
        cpu_shares=min(requested.cpu_shares, tier_max.cpu_shares),
        max_output_bytes=min(requested.max_output_bytes, tier_max.max_output_bytes),
        max_log_lines=min(requested.max_log_lines, tier_max.max_log_lines),
    )
