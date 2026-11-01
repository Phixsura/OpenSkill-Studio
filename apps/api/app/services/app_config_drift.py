"""App Config Drift — detect configuration drift between environments.

Compares configurations across environments:
- Snapshot environment configs
- Detect drifted keys (added, removed, changed)
- Track drift history
- Per-installation scoped configs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DriftEntry:
    """A single config drift."""

    key: str
    drift_type: str  # "added", "removed", "changed"
    source_value: str | None = None
    target_value: str | None = None


@dataclass
class DriftReport:
    """Drift comparison between two environments."""

    source_env: str
    target_env: str
    drifts: list[DriftEntry]
    checked_at: float = field(default_factory=time.time)

    @property
    def drift_count(self) -> int:
        return len(self.drifts)

    @property
    def has_drift(self) -> bool:
        return len(self.drifts) > 0


class AppConfigDrift:
    """Detect configuration drift between environments."""

    def __init__(self) -> None:
        # (installation_id, env) → config dict
        self._configs: dict[tuple[str, str], dict[str, str]] = {}
        self._reports: dict[tuple[str, str, str], DriftReport] = {}

    def snapshot(
        self, installation_id: str, env: str, config: dict[str, str],
    ) -> dict[str, str]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not env:
            raise ValueError("env is required")
        self._configs[(installation_id, env)] = dict(config)
        return config

    def compare(
        self, installation_id: str, source_env: str, target_env: str,
    ) -> DriftReport:
        src = self._configs.get((installation_id, source_env))
        tgt = self._configs.get((installation_id, target_env))
        if src is None:
            raise KeyError(f"No config snapshot for env '{source_env}'")
        if tgt is None:
            raise KeyError(f"No config snapshot for env '{target_env}'")

        drifts: list[DriftEntry] = []

        all_keys = sorted(set(src.keys()) | set(tgt.keys()))
        for key in all_keys:
            in_src = key in src
            in_tgt = key in tgt
            if in_src and not in_tgt:
                drifts.append(DriftEntry(key=key, drift_type="removed", source_value=src[key]))
            elif not in_src and in_tgt:
                drifts.append(DriftEntry(key=key, drift_type="added", target_value=tgt[key]))
            elif src[key] != tgt[key]:
                drifts.append(DriftEntry(key=key, drift_type="changed", source_value=src[key], target_value=tgt[key]))

        report = DriftReport(source_env=source_env, target_env=target_env, drifts=drifts)
        self._reports[(installation_id, source_env, target_env)] = report
        return report

    def get_config(self, installation_id: str, env: str) -> dict[str, str]:
        cfg = self._configs.get((installation_id, env))
        if cfg is None:
            raise KeyError(f"No config for env '{env}'")
        return dict(cfg)

    def list_envs(self, installation_id: str) -> list[str]:
        return sorted(env for (inst, env) in self._configs if inst == installation_id)
