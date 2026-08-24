"""Untrusted text hygiene (ADR-010 D10).

Applied to any third-party string before it enters reports, prompts, or
stored metadata: ComfyUI node titles, pack descriptions entering LLM
prompts, raw natural-language requests.

Defends against ASCII smuggling (Unicode Tags block), zero-width payloads,
bidi spoofing, and control-character injection.
"""

import re
import unicodedata

# Invisible / reordering characters that survive NFKC (explicit escapes so
# this source file itself contains no invisible characters):
# - Unicode Tags block U+E0000-U+E007F (ASCII smuggling)
# - Zero-width: ZWSP U+200B, ZWNJ U+200C, ZWJ U+200D, BOM U+FEFF, WJ U+2060
# - Bidi controls: LRE..RLO U+202A-U+202E, isolates LRI..PDI U+2066-U+2069
_INVISIBLE_RE = re.compile(
    "["
    "\U000e0000-\U000e007f"
    "​-‍"
    "﻿"
    "⁠"
    "‪-‮"
    "⁦-⁩"
    "]"
)

# C0/C1 control characters except \t (U+0009) and \n (U+000A)
_CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def sanitize_untrusted_text(s: str, max_len: int = 1000) -> str:
    """Normalize and strip invisible/control characters, then truncate."""
    if not s:
        return ""
    # Pre-slice BEFORE normalization: NFKC on a hostile multi-MB string costs
    # seconds of CPU (U+FDFA expands 18x) just to throw it away at truncation.
    # 8x headroom covers any contracting sequences (invisible chars stripped
    # below plus combining-mark folds) so the visible output still reaches
    # max_len for legitimate input.
    s = s[: max_len * 8]
    s = unicodedata.normalize("NFKC", s)
    s = _INVISIBLE_RE.sub("", s)
    s = _CTRL_RE.sub("", s)
    return s[:max_len]
