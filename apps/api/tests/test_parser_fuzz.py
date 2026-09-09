"""R194: Hypothesis property fuzz over the pure parsers that consume
attacker-controlled bytes/text (industry technique: generative fuzzing —
found the _parse_semver totality gap the hand-written probes missed)."""

import struct

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.core.genmeta import (
    extract_generation_metadata,
    extract_png_text_chunks,
    parse_a1111_infotext,
    parse_comfyui_prompt,
)
from app.core.sanitize import sanitize_untrusted_text
from app.services.workflow_pack import _parse_semver

_FUZZ = settings(max_examples=200, suppress_health_check=list(HealthCheck), deadline=None)


@_FUZZ
@given(st.binary(max_size=4096))
def test_png_extractor_total_over_bytes(data):
    extract_png_text_chunks(data)
    extract_generation_metadata(data, "image/png")


@_FUZZ
@given(
    st.lists(
        st.tuples(
            st.sampled_from([b"tEXt", b"zTXt", b"iTXt", b"IDAT", b"IEND"]),
            st.binary(max_size=200),
        ),
        max_size=8,
    )
)
def test_png_extractor_total_over_hostile_chunks(chunks):
    data = b"\x89PNG\r\n\x1a\n"
    for ctype, payload in chunks:
        data += struct.pack(">I", len(payload)) + ctype + payload + b"\x00\x00\x00\x00"
    extract_png_text_chunks(data)


@_FUZZ
@given(st.text(max_size=3000))
def test_infotext_parsers_total_over_text(t):
    parse_a1111_infotext(t)
    parse_comfyui_prompt(t)


@_FUZZ
@given(st.text(max_size=60))
def test_parse_semver_total(v):
    """'' → ValueError and '0' → IndexError before R194. Every API path is
    schema-gated, but registry sorting reads STORED versions — the helper
    must be total (malformed sorts lowest)."""
    key = _parse_semver(v)
    assert isinstance(key, tuple) and len(key) == 4


def test_parse_semver_malformed_sorts_lowest():
    assert _parse_semver("garbage") < _parse_semver("0.0.0-0")
    assert _parse_semver("1.2.10") > _parse_semver("1.2.9")


@_FUZZ
@given(st.text(max_size=5000), st.integers(min_value=1, max_value=2000))
def test_sanitize_total_and_bounded(t, n):
    out = sanitize_untrusted_text(t, n)
    assert len(out) <= n
