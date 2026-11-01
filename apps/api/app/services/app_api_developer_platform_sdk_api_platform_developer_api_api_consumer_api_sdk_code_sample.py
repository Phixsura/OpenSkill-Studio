"""API Consumer SDK Code Sample — generate code samples for API endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CodeSample:
    sample_id: str
    endpoint: str
    method: str
    language: str  # "python", "typescript", "curl", "go", "ruby"
    code: str
    description: str = ""

VALID_LANGUAGES = {"python", "typescript", "javascript", "curl", "go", "ruby", "java", "csharp", "php"}

TEMPLATES: dict[str, str] = {
    "curl": 'curl -X {method} "{base_url}{endpoint}" \\\n  -H "Authorization: Bearer $API_KEY" \\\n  -H "Content-Type: application/json"',
    "python": 'import requests\n\nresponse = requests.{method_lower}(\n    "{base_url}{endpoint}",\n    headers={{"Authorization": "Bearer " + api_key}},\n)\nprint(response.json())',
    "typescript": 'const response = await fetch("{base_url}{endpoint}", {{\n  method: "{method}",\n  headers: {{ "Authorization": `Bearer ${{apiKey}}` }},\n}});\nconst data = await response.json();',
}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample:
    def __init__(self, base_url: str = "https://api.example.com") -> None:
        self._samples: dict[tuple[str, str], list[CodeSample]] = {}
        self._base_url = base_url

    def generate(self, installation_id: str, endpoint: str, method: str, language: str) -> CodeSample:
        if not installation_id: raise ValueError("installation_id is required")
        if language not in VALID_LANGUAGES: raise ValueError(f"Invalid language: {language}")
        template = TEMPLATES.get(language, TEMPLATES.get("curl", ""))
        code = template.format(method=method.upper(), method_lower=method.lower(), endpoint=endpoint, base_url=self._base_url)
        sample = CodeSample(sample_id=f"{method}-{endpoint}-{language}", endpoint=endpoint, method=method.upper(), language=language, code=code)
        self._samples.setdefault((installation_id, endpoint), []).append(sample)
        return sample

    def add_custom(self, installation_id: str, sample: CodeSample) -> CodeSample:
        if not installation_id: raise ValueError("installation_id is required")
        if sample.language not in VALID_LANGUAGES: raise ValueError(f"Invalid language: {sample.language}")
        self._samples.setdefault((installation_id, sample.endpoint), []).append(sample)
        return sample

    def samples_for(self, installation_id: str, endpoint: str) -> list[CodeSample]:
        return self._samples.get((installation_id, endpoint), [])

    def languages_available(self, installation_id: str, endpoint: str) -> list[str]:
        return list({s.language for s in self._samples.get((installation_id, endpoint), [])})

    def total_samples(self, installation_id: str) -> int:
        return sum(len(s) for (inst, _), s in self._samples.items() if inst == installation_id)
