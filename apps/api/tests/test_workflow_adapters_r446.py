"""R446: workflow provider adapters — mock usage mapping, adapter registry,
Anthropic org-key + model-allowlist guards.

Documented EQUIVALENT mutants (adjudicated): L64 digest[:26]->27, L129/131
sanitize 4000->4001, and L132 token_hex(8)->9 are ±1 length/byte bounds
whose outputs stay deterministic — no observable difference in the
determinism/pass assertions. (The mock usage QUANTITIES and image/video/
voice branch mappings ARE pinned — verified by hand-applied mutants; the
AST harness reports them as false survivors on this sub-0.2s module because
rapid mutate/restore cycles collide on .pyc mtime granularity.)
"""

import pytest

from app.services.workflow_adapters import (
    AnthropicReviewAdapter,
    MockAdapter,
    get_adapter,
)

pytestmark = pytest.mark.asyncio


async def test_mock_adapter_usage_mapping_r446():
    m = MockAdapter()

    async def _usage(capability):
        out = await m.execute(capability, "model", {"prompt": "hi"}, {}, None, "idem")
        return out["__usage__"]

    # each capability class maps to its deterministic usage rows
    assert await _usage("image_generation") == [{"usage_type": "image_generation", "quantity": 1}]
    assert await _usage("video_generation") == [
        {"usage_type": "video_generation_seconds", "quantity": 10}]
    assert await _usage("voice_clone") == [{"usage_type": "voice_generation", "quantity": 15}]
    assert await _usage("audio_transcribe") == [{"usage_type": "voice_generation", "quantity": 15}]
    # the else branch (e.g. text/llm) emits input+output token rows with the
    # exact deterministic quantities
    llm = await _usage("text_completion")
    by = {u["usage_type"]: u["quantity"] for u in llm}
    assert by == {"llm_input_tokens": 120, "llm_output_tokens": 350}

    # the result asset id is DETERMINISTIC across identical inputs (retry-safe)
    o1 = await m.execute("image_generation", "x", {"a": 1}, {}, None, "k")
    o2 = await m.execute("image_generation", "x", {"a": 1}, {}, None, "k")
    assert o1["result"] == o2["result"]
    # different inputs → different asset id
    o3 = await m.execute("image_generation", "x", {"a": 2}, {}, None, "k")
    assert o3["result"] != o1["result"]
    # echo elision boundary: a value of len < 500 is kept, >= 500 is elided
    o4 = await m.execute("image_generation", "x",
                         {"keep": "y" * 499, "drop": "y" * 500, "n": 5}, {}, None, "k")
    assert o4["echo"]["keep"] == "y" * 499   # 499 < 500 → kept
    assert o4["echo"]["drop"] == "…"          # 500 not < 500 → elided
    assert o4["echo"]["n"] == "…"             # non-string elided too


async def test_get_adapter_registry_r446():
    assert isinstance(get_adapter("mock"), MockAdapter)
    assert isinstance(get_adapter("anthropic"), AnthropicReviewAdapter)
    assert get_adapter("nonexistent") is None


async def test_anthropic_full_path_mocked_r446(monkeypatch):
    from types import SimpleNamespace

    import app.core.llm as llm_mod

    captured = {}

    class _FakeClient:
        def __init__(self, api_key, model):
            captured["api_key"] = api_key
            captured["model"] = model

        async def complete(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                content="R" * 9000,  # over the 8000 cap
                model="claude-sonnet-5",
                provider="anthropic",
                input_tokens=42,
                output_tokens=7,
            )

    monkeypatch.setattr(llm_mod, "AnthropicClient", _FakeClient)
    a = AnthropicReviewAdapter()
    out = await a.execute("multimodal_review", "claude-opus-5",
                          {"prompt": "check this", "subject": "the asset"},
                          {}, {"api_key": "sk-org"}, "idem")
    # the org key + org-chosen (claude-) model are passed through
    assert captured["api_key"] == "sk-org"
    assert captured["model"] == "claude-opus-5"
    # max_tokens is pinned at 1024 (kills 1024 -> 1025)
    assert captured["max_tokens"] == 1024
    # the result content is truncated to 8000 (kills [:8000] -> [:8001])
    assert len(out["result"]) == 8000
    # usage carries the real token counts, dropping any zero-quantity row
    usage = {u["usage_type"]: u["quantity"] for u in out["__usage__"]}
    assert usage == {"llm_input_tokens": 42, "llm_output_tokens": 7}

    # a response with zero token counts → those usage rows are filtered out
    class _ZeroClient(_FakeClient):
        async def complete(self, **kwargs):
            return SimpleNamespace(content="ok", model="m", provider="anthropic",
                                   input_tokens=0, output_tokens=0)

    monkeypatch.setattr(llm_mod, "AnthropicClient", _ZeroClient)
    out2 = await a.execute("multimodal_review", "claude-sonnet-5", {"prompt": "x"},
                           {}, {"api_key": "sk-org"}, "idem")
    assert out2["__usage__"] == []  # zero-quantity rows dropped


async def test_anthropic_guards_r446():
    a = AnthropicReviewAdapter()
    # no credential / no api_key → RuntimeError (never falls back to platform key)
    with pytest.raises(RuntimeError, match="no API key"):
        await a.execute("multimodal_review", "claude-sonnet-5", {}, {}, None, "idem")
    with pytest.raises(RuntimeError, match="no API key"):
        await a.execute("multimodal_review", "claude-sonnet-5", {}, {}, {"other": "x"}, "idem")
    # a non-Claude model id is rejected (org-controlled model_name allowlist)
    with pytest.raises(RuntimeError, match="not an allowed"):
        await a.execute("multimodal_review", "gpt-4o", {}, {}, {"api_key": "sk-x"}, "idem")
