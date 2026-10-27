"""Config Flags — hierarchical feature flags with environment overrides.

Implements:
- Flag hierarchy: default < environment < tenant < user
- Boolean, string, and JSON flag values
- Percentage rollout with consistent bucketing
- Flag dependencies (flag A requires flag B)
- Audit trail of flag changes
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class FlagValue:
    value: object
    source: str  # default, environment, tenant, user
    set_at: float = 0.0


@dataclass
class FlagDef:
    name: str
    default_value: object
    flag_type: str = "boolean"  # boolean, string, json, number
    description: str = ""
    requires: list[str] = field(default_factory=list)  # dependent flags
    rollout_pct: int = 100
    overrides: dict[str, FlagValue] = field(default_factory=dict)  # scope → value


class ConfigFlagsService:
    def __init__(self):
        self._flags: dict[str, FlagDef] = {}
        self._audit: list[dict] = []

    def define(self, name: str, default: object, flag_type: str = "boolean",
               description: str = "", requires: list[str] | None = None,
               rollout_pct: int = 100) -> FlagDef:
        flag = FlagDef(name=name, default_value=default, flag_type=flag_type,
                       description=description, requires=requires or [],
                       rollout_pct=rollout_pct)
        self._flags[name] = flag
        return flag

    def set_override(self, flag_name: str, scope: str,
                     value: object, source: str = "manual") -> bool:
        """Set flag value for a specific scope (env:prod, tenant:acme, user:123)."""
        flag = self._flags.get(flag_name)
        if not flag:
            return False
        flag.overrides[scope] = FlagValue(value=value, source=source,
                                          set_at=time.time())
        self._audit.append({"flag": flag_name, "scope": scope,
                            "value": value, "source": source,
                            "timestamp": time.time()})
        return True

    def evaluate(self, flag_name: str, context: dict | None = None) -> object:
        """Evaluate flag value for a given context.
        context: {environment, tenant_id, user_id}"""
        flag = self._flags.get(flag_name)
        if not flag:
            return None
        context = context or {}

        # Check dependencies
        for req in flag.requires:
            if not self.evaluate(req, context):
                return flag.default_value if flag.flag_type != "boolean" else False

        # Rollout check
        if flag.rollout_pct < 100:
            user_id = context.get("user_id", "")
            if user_id:
                h = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest()[:8], 16)
                if (h % 100) >= flag.rollout_pct:
                    return flag.default_value

        # Override hierarchy: user > tenant > environment > default
        user_scope = f"user:{context.get('user_id', '')}"
        tenant_scope = f"tenant:{context.get('tenant_id', '')}"
        env_scope = f"env:{context.get('environment', '')}"

        for scope in [user_scope, tenant_scope, env_scope]:
            if scope in flag.overrides:
                return flag.overrides[scope].value

        return flag.default_value

    def is_enabled(self, flag_name: str, context: dict | None = None) -> bool:
        """Convenience for boolean flags."""
        return bool(self.evaluate(flag_name, context))

    def get_all(self, context: dict | None = None) -> dict[str, object]:
        """Evaluate all flags for a context."""
        return {name: self.evaluate(name, context) for name in self._flags}

    def get_audit(self, flag_name: str = "", limit: int = 50) -> list[dict]:
        entries = self._audit
        if flag_name:
            entries = [e for e in entries if e["flag"] == flag_name]
        return entries[-limit:]

    def list_flags(self) -> list[dict]:
        return [{"name": f.name, "type": f.flag_type, "default": f.default_value,
                 "rollout_pct": f.rollout_pct, "overrides": len(f.overrides)}
                for f in self._flags.values()]
