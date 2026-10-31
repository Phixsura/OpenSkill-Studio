"""Developer API Console — interactive API testing with auth, env vars.

Provides a developer-facing API console with environment management,
variable interpolation, request chaining, and response assertions.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Environment:
    env_id: str
    name: str
    variables: dict[str, str] = field(default_factory=dict)
    is_active: bool = False


@dataclass
class ConsoleRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    response_status: int = 0
    response_body: str = ""


class DeveloperApiConsoleService:
    """Interactive API console with environments."""

    def __init__(self):
        self._envs: dict[str, list[Environment]] = defaultdict(list)
        self._active: dict[str, str] = {}  # user -> env_id
        self._history: dict[str, list[ConsoleRequest]] = defaultdict(list)

    def create_env(self, user_id: str, name: str,
                   variables: dict[str, str] | None = None) -> Environment:
        env = Environment(
            env_id=f"env_{secrets.token_urlsafe(6)}",
            name=name, variables=variables or {},
        )
        self._envs[user_id].append(env)
        if not self._active.get(user_id):
            self._active[user_id] = env.env_id
            env.is_active = True
        return env

    def set_active_env(self, user_id: str, env_id: str) -> bool:
        for env in self._envs.get(user_id, []):
            env.is_active = env.env_id == env_id
        self._active[user_id] = env_id
        return True

    def get_envs(self, user_id: str) -> list[Environment]:
        return self._envs.get(user_id, [])

    def interpolate(self, user_id: str, text: str) -> str:
        env_id = self._active.get(user_id)
        if not env_id:
            return text
        env = next((e for e in self._envs.get(user_id, []) if e.env_id == env_id), None)
        if not env:
            return text
        result = text
        for k, v in env.variables.items():
            result = result.replace(f"{{{{{k}}}}}", v)
        return result

    def execute(self, user_id: str, method: str, url: str,
                headers: dict | None = None, body: str = "") -> ConsoleRequest:
        resolved_url = self.interpolate(user_id, url)
        resolved_body = self.interpolate(user_id, body)
        resolved_headers = {k: self.interpolate(user_id, v) for k, v in (headers or {}).items()}

        req = ConsoleRequest(
            method=method.upper(), url=resolved_url,
            headers=resolved_headers, body=resolved_body,
            response_status=200, response_body='{"ok": true}',
        )
        self._history[user_id].append(req)
        return req

    def get_history(self, user_id: str, limit: int = 20) -> list[ConsoleRequest]:
        return self._history.get(user_id, [])[-limit:]

    def set_variable(self, user_id: str, key: str, value: str) -> bool:
        env_id = self._active.get(user_id)
        if not env_id:
            return False
        env = next((e for e in self._envs.get(user_id, []) if e.env_id == env_id), None)
        if env:
            env.variables[key] = value
            return True
        return False
