"""CLI Generator — generate CLI tool scaffolding for extension development.

Creates project scaffolding with manifest, entrypoint, test files,
CI config, and README for different runtimes and extension types.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class GeneratedFile:
    path: str
    content: str
    executable: bool = False


@dataclass
class ScaffoldResult:
    extension_name: str
    runtime: str
    files: list[GeneratedFile] = field(default_factory=list)
    total_files: int = 0


RUNTIME_CONFIGS: dict[str, dict] = {
    "node20": {
        "entrypoint": "src/index.ts",
        "test_file": "tests/index.test.ts",
        "config_file": "package.json",
        "extension": ".ts",
    },
    "python3.12": {
        "entrypoint": "src/main.py",
        "test_file": "tests/test_main.py",
        "config_file": "pyproject.toml",
        "extension": ".py",
    },
    "deno": {
        "entrypoint": "src/mod.ts",
        "test_file": "tests/mod_test.ts",
        "config_file": "deno.json",
        "extension": ".ts",
    },
}


class CLIGeneratorService:
    """Generates extension project scaffolding."""

    def scaffold(self, name: str, runtime: str,
                 extension_type: str = "basic",
                 description: str = "") -> ScaffoldResult:
        if runtime not in RUNTIME_CONFIGS:
            raise ValueError(f"Unsupported runtime: {runtime}")
        if not name or not name.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Invalid extension name")

        config = RUNTIME_CONFIGS[runtime]
        files: list[GeneratedFile] = []

        # Manifest
        files.append(GeneratedFile(
            path="manifest.json",
            content=self._gen_manifest(name, runtime, description, config),
        ))

        # Entrypoint
        files.append(GeneratedFile(
            path=config["entrypoint"],
            content=self._gen_entrypoint(name, runtime, extension_type),
        ))

        # Test
        files.append(GeneratedFile(
            path=config["test_file"],
            content=self._gen_test(name, runtime),
        ))

        # Config
        files.append(GeneratedFile(
            path=config["config_file"],
            content=self._gen_config(name, runtime, description),
        ))

        # README
        files.append(GeneratedFile(
            path="README.md",
            content=self._gen_readme(name, runtime, description),
        ))

        # .gitignore
        files.append(GeneratedFile(
            path=".gitignore",
            content=self._gen_gitignore(runtime),
        ))

        result = ScaffoldResult(
            extension_name=name, runtime=runtime,
            files=files, total_files=len(files),
        )
        return result

    def _gen_manifest(self, name: str, runtime: str, desc: str, config: dict) -> str:
        import json
        return json.dumps({
            "name": name, "version": "0.1.0",
            "manifest_version": "2.0",
            "runtime": runtime,
            "entrypoint": config["entrypoint"],
            "description": desc or f"{name} extension",
            "permissions": ["storage:local"],
            "sdk_version": "1.0.0",
        }, indent=2)

    def _gen_entrypoint(self, name: str, runtime: str, ext_type: str) -> str:
        if runtime.startswith("python"):
            return f'"""Extension: {name}"""\n\ndef activate(context):\n    print(f"{name} activated")\n    return {{"status": "ok"}}\n\ndef deactivate():\n    print(f"{name} deactivated")\n'
        return f'// Extension: {name}\n\nexport function activate(context) {{\n  console.log("{name} activated");\n  return {{ status: "ok" }};\n}}\n\nexport function deactivate() {{\n  console.log("{name} deactivated");\n}}\n'

    def _gen_test(self, name: str, runtime: str) -> str:
        if runtime.startswith("python"):
            return f'from src.main import activate, deactivate\n\ndef test_activate():\n    result = activate({{}})\n    assert result["status"] == "ok"\n\ndef test_deactivate():\n    deactivate()  # should not raise\n'
        return f'import {{ activate, deactivate }} from "../src/index";\n\ntest("{name} activates", () => {{\n  const result = activate({{}});\n  expect(result.status).toBe("ok");\n}});\n'

    def _gen_config(self, name: str, runtime: str, desc: str) -> str:
        import json
        if runtime.startswith("python"):
            return f'[project]\nname = "{name}"\nversion = "0.1.0"\ndescription = "{desc}"\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
        if runtime == "deno":
            return json.dumps({"tasks": {"test": "deno test"}}, indent=2)
        return json.dumps({
            "name": name, "version": "0.1.0",
            "scripts": {"test": "vitest run", "build": "tsc"},
        }, indent=2)

    def _gen_readme(self, name: str, runtime: str, desc: str) -> str:
        return f"# {name}\n\n{desc or 'An OpenSkill extension.'}\n\n## Getting Started\n\n```bash\n# Install dependencies\nnpm install  # or uv sync\n\n# Run tests\nnpm test\n```\n\n## Runtime\n\n{runtime}\n"

    def _gen_gitignore(self, runtime: str) -> str:
        base = "node_modules/\ndist/\n.env\n*.log\n"
        if runtime.startswith("python"):
            base += ".venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n"
        return base

    def list_templates(self) -> list[dict]:
        return [{"runtime": rt, "entrypoint": cfg["entrypoint"]}
                for rt, cfg in RUNTIME_CONFIGS.items()]
