"""Provider adapter implementations (ADR-011).

Adapters implement a single async execute() contract. They receive decrypted
credentials ONLY here — at call time, inside the executor — never earlier.

Phase 1 ships two adapters:
- MockAdapter: deterministic echo for tests/demos (no network, no credentials)
- AnthropicReviewAdapter: multimodal_review via the existing LLM client
"""

import hashlib
import json
from abc import ABC, abstractmethod

import structlog

log = structlog.get_logger()


class ProviderAdapterBase(ABC):
    """Contract: bounded, single-call execution. No retries here (runtime owns retry)."""

    key: str = ""

    @abstractmethod
    async def execute(
        self,
        capability: str,
        model_name: str,
        inputs: dict,
        config: dict,
        credentials: dict[str, str] | None,
        idempotency_key: str,
    ) -> dict:
        """Execute one provider call. Returns a JSON-safe output dict (≤48KB)."""


class MockAdapter(ProviderAdapterBase):
    """Deterministic echo adapter — same inputs always produce the same output.

    Used for tests, demos, and local development without any provider account.
    """

    key = "mock"

    async def execute(
        self,
        capability: str,
        model_name: str,
        inputs: dict,
        config: dict,
        credentials: dict[str, str] | None,
        idempotency_key: str,
    ) -> dict:
        # Deterministic pseudo-asset id derived from inputs (stable across retries)
        digest = hashlib.sha256(
            json.dumps({"cap": capability, "in": inputs}, sort_keys=True).encode()
        ).hexdigest()[:26]
        return {
            "result": f"mock-asset-{digest}",
            "capability": capability,
            "model": model_name,
            "echo": {k: (v if isinstance(v, str) and len(v) < 500 else "…") for k, v in inputs.items()},
        }


class AnthropicReviewAdapter(ProviderAdapterBase):
    """multimodal_review capability via the existing LLM client (create_llm_client)."""

    key = "anthropic"

    async def execute(
        self,
        capability: str,
        model_name: str,
        inputs: dict,
        config: dict,
        credentials: dict[str, str] | None,
        idempotency_key: str,
    ) -> dict:
        from app.core.llm import create_llm_client

        # Note: Phase 1 uses the platform-level LLM key from settings; the
        # org credential (if provided) is reserved for Phase 2 per-org keys.
        client = create_llm_client(model_name or None)
        prompt_text = str(inputs.get("prompt", "Review the provided content."))[:4000]
        subject = str(inputs.get("subject", ""))[:4000]
        response = await client.complete(
            system_prompt=(
                "You are a production QA reviewer. Return a concise JSON object "
                'with keys "verdict" (pass|revise), "notes" (string).'
            ),
            user_prompt=f"{prompt_text}\n\nContent reference:\n{subject}",
            max_tokens=1024,
            temperature=0.0,
        )
        return {
            "result": response.content[:8000],
            "model": response.model,
            "provider": response.provider,
        }


_ADAPTERS: dict[str, ProviderAdapterBase] = {
    "mock": MockAdapter(),
    "anthropic": AnthropicReviewAdapter(),
}


def get_adapter(key: str) -> ProviderAdapterBase | None:
    return _ADAPTERS.get(key)
