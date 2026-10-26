"""Sandbox Module Loader — secure module resolution for extension sandboxes.

Controls which modules extensions can import, manages module allowlists,
blocks dangerous modules, and tracks import usage.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


BLOCKED_MODULES = {
    "os", "sys", "subprocess", "shutil", "ctypes", "importlib",
    "socket", "http", "urllib", "ftplib", "telnetlib", "smtplib",
    "pickle", "shelve", "marshal", "code", "codeop", "compile",
    "child_process", "fs", "net", "cluster", "dgram", "dns",
    "process", "v8", "vm", "worker_threads",
}

BUILTIN_ALLOWED = {
    "json", "math", "re", "datetime", "collections", "itertools",
    "functools", "hashlib", "hmac", "base64", "uuid", "typing",
    "dataclasses", "enum", "abc", "copy", "io", "string",
    "textwrap", "difflib", "unicodedata", "time",
    # Node built-ins
    "path", "url", "querystring", "crypto", "buffer", "events",
    "stream", "util", "assert", "console",
}


@dataclass
class ModuleImport:
    module_name: str
    allowed: bool
    reason: str


class SandboxModuleLoaderService:
    """Controls module imports in extension sandboxes."""

    def __init__(self):
        self._custom_allowlist: dict[str, set[str]] = defaultdict(set)
        self._import_log: dict[str, list[ModuleImport]] = defaultdict(list)
        self._blocked_count: dict[str, int] = defaultdict(int)

    def add_to_allowlist(self, sandbox_id: str, modules: list[str]) -> int:
        added = 0
        for mod in modules:
            if mod in BLOCKED_MODULES:
                continue  # cannot override blocked
            self._custom_allowlist[sandbox_id].add(mod)
            added += 1
        return added

    def can_import(self, sandbox_id: str, module_name: str) -> ModuleImport:
        # Strip submodules for top-level check
        top_level = module_name.split(".")[0]

        if top_level in BLOCKED_MODULES:
            result = ModuleImport(module_name, False, f"Blocked: {top_level} is restricted")
            self._blocked_count[sandbox_id] += 1
            self._import_log[sandbox_id].append(result)
            return result

        if top_level in BUILTIN_ALLOWED:
            result = ModuleImport(module_name, True, "Built-in allowed")
            self._import_log[sandbox_id].append(result)
            return result

        custom = self._custom_allowlist.get(sandbox_id, set())
        if top_level in custom:
            result = ModuleImport(module_name, True, "Custom allowlist")
            self._import_log[sandbox_id].append(result)
            return result

        result = ModuleImport(module_name, False, "Not in allowlist")
        self._blocked_count[sandbox_id] += 1
        self._import_log[sandbox_id].append(result)
        return result

    def get_import_log(self, sandbox_id: str) -> list[ModuleImport]:
        return self._import_log.get(sandbox_id, [])

    def get_blocked_count(self, sandbox_id: str) -> int:
        return self._blocked_count.get(sandbox_id, 0)

    def get_allowlist(self, sandbox_id: str) -> dict:
        return {
            "builtin": sorted(BUILTIN_ALLOWED),
            "custom": sorted(self._custom_allowlist.get(sandbox_id, set())),
            "blocked": sorted(BLOCKED_MODULES),
        }
