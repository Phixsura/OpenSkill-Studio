"""Sandbox Template Engine — pre-built sandbox environments for quick start."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SandboxTemplate:
    template_id: str
    name: str
    runtime: str  # python, node, deno, go
    files: dict[str, str] = field(default_factory=dict)  # path -> content
    env_vars: dict[str, str] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    description: str = ""
    category: str = "general"


class SandboxTemplateEngineService:
    def __init__(self):
        self._templates: dict[str, SandboxTemplate] = {}
        self._seed()

    def _seed(self):
        self._templates["python-basic"] = SandboxTemplate(
            template_id="python-basic", name="Python Basic", runtime="python",
            files={"main.py": "print('Hello from sandbox!')", "requirements.txt": ""},
            category="starter", description="Basic Python sandbox")
        self._templates["node-api"] = SandboxTemplate(
            template_id="node-api", name="Node.js API", runtime="node",
            files={"index.js": "console.log('API ready');", "package.json": "{}"},
            dependencies=["express"], category="api", description="Node.js API template")

    def get(self, template_id: str) -> SandboxTemplate | None:
        return self._templates.get(template_id)

    def list_all(self, category: str | None = None) -> list[SandboxTemplate]:
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    def create(self, template_id: str, name: str, runtime: str,
               files: dict[str, str], **kwargs) -> SandboxTemplate:
        t = SandboxTemplate(template_id=template_id, name=name,
                            runtime=runtime, files=files, **kwargs)
        self._templates[template_id] = t
        return t

    def instantiate(self, template_id: str, overrides: dict[str, str] | None = None) -> dict:
        t = self._templates.get(template_id)
        if not t:
            return {"error": "Template not found"}
        files = dict(t.files)
        if overrides:
            files.update(overrides)
        return {"runtime": t.runtime, "files": files, "env_vars": t.env_vars,
                "dependencies": t.dependencies}

    def get_runtimes(self) -> list[str]:
        return list({t.runtime for t in self._templates.values()})
