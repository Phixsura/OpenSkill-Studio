"""Sandbox Env Inspector — inspect sandbox runtime environment details.

Provides runtime info, installed packages, available APIs, system
limits, and environment diagnostics for extension debugging.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class InstalledPackage:
    name: str
    version: str
    size_kb: int = 0


@dataclass
class SystemLimit:
    name: str
    current: int | float
    max_value: int | float
    unit: str = ""


@dataclass
class EnvInspection:
    sandbox_id: str
    runtime: str
    runtime_version: str
    packages: list[InstalledPackage] = field(default_factory=list)
    available_apis: list[str] = field(default_factory=list)
    limits: list[SystemLimit] = field(default_factory=list)
    env_vars_count: int = 0
    diagnostics: list[str] = field(default_factory=list)


class SandboxEnvInspectorService:
    """Inspects sandbox environment for debugging."""

    def __init__(self):
        self._inspections: dict[str, EnvInspection] = {}

    def inspect(self, sandbox_id: str, runtime: str, runtime_version: str,
                packages: list[dict] | None = None,
                available_apis: list[str] | None = None,
                limits: list[dict] | None = None,
                env_vars_count: int = 0) -> EnvInspection:
        parsed_pkgs = [InstalledPackage(
            name=p["name"], version=p["version"],
            size_kb=p.get("size_kb", 0),
        ) for p in (packages or [])]

        parsed_limits = [SystemLimit(
            name=l["name"], current=l["current"],
            max_value=l["max"], unit=l.get("unit", ""),
        ) for l in (limits or [])]

        # Run diagnostics
        diagnostics = self._run_diagnostics(parsed_pkgs, parsed_limits, available_apis or [])

        inspection = EnvInspection(
            sandbox_id=sandbox_id, runtime=runtime,
            runtime_version=runtime_version,
            packages=parsed_pkgs, available_apis=available_apis or [],
            limits=parsed_limits, env_vars_count=env_vars_count,
            diagnostics=diagnostics,
        )
        self._inspections[sandbox_id] = inspection
        return inspection

    def _run_diagnostics(self, packages: list[InstalledPackage],
                         limits: list[SystemLimit],
                         apis: list[str]) -> list[str]:
        issues = []
        # Check for common issues
        total_size = sum(p.size_kb for p in packages)
        if total_size > 100 * 1024:  # 100MB
            issues.append(f"Large package footprint: {total_size // 1024}MB")
        for limit in limits:
            usage_pct = limit.current / max(limit.max_value, 1) * 100
            if usage_pct > 80:
                issues.append(f"{limit.name} at {usage_pct:.0f}% capacity")
        if not apis:
            issues.append("No APIs available — check permissions")
        return issues

    def get_inspection(self, sandbox_id: str) -> EnvInspection | None:
        return self._inspections.get(sandbox_id)

    def search_packages(self, sandbox_id: str, query: str) -> list[InstalledPackage]:
        inspection = self._inspections.get(sandbox_id)
        if not inspection:
            return []
        q = query.lower()
        return [p for p in inspection.packages if q in p.name.lower()]

    def check_api_available(self, sandbox_id: str, api_name: str) -> bool:
        inspection = self._inspections.get(sandbox_id)
        if not inspection:
            return False
        return api_name in inspection.available_apis

    def get_summary(self, sandbox_id: str) -> dict:
        inspection = self._inspections.get(sandbox_id)
        if not inspection:
            return {}
        return {
            "runtime": f"{inspection.runtime} {inspection.runtime_version}",
            "packages": len(inspection.packages),
            "apis": len(inspection.available_apis),
            "limits": len(inspection.limits),
            "env_vars": inspection.env_vars_count,
            "issues": len(inspection.diagnostics),
        }
