"""R429: comfyui-import dependency report + NUL scan (untrusted graph parsing).

_build_dependency_report classifies on the RAW class_type (R86): a
fold-disguised custom node (fullwidth 'ＫSampler' → NFKC 'KSampler') must
NOT be mis-counted as a trusted core node and erased from the custom-node
warning. _parsed_has_nul closes a JSONB 500 on NUL bytes. Both pure → fast.

Documented EQUIVALENT mutants (adjudicated): L412/L427/L441/L444
truncation/cap bounds (120-char class_type, 300-char filename, [:500]
custom-node list, [:100] model list) ±1 are one-element/one-char bound
changes on already-bounded output (true totals preserved separately); L413
`class_counts[ct] += 1` accumulates a dict never returned in the report
(core_count derives from custom_counts) — no observable effect.
"""

from app.services.comfyui_import import (
    ComfyUIImportService as Ci,
)
from app.services.comfyui_import import (
    _parsed_has_nul,
)


def _node(class_type, widgets=None):
    return {"class_type": class_type, "widgets_values": widgets or []}


def test_parsed_has_nul_r429():
    assert _parsed_has_nul("clean") is False
    assert _parsed_has_nul("with\x00nul") is True
    # NUL in a dict KEY and in a nested list value
    assert _parsed_has_nul({"k\x00": "v"}) is True
    assert _parsed_has_nul({"ok": ["fine", {"deep": "n\x00o"}]}) is True
    # other control chars are tolerated here (only NUL matters for JSONB)
    assert _parsed_has_nul("tab\tnewline\n") is False
    # deep nesting does not recurse-crash
    v = []
    cur = v
    for _ in range(2000):
        nxt = []
        cur.append(nxt)
        cur = nxt
    cur.append("x\x00")
    assert _parsed_has_nul(v) is True


def test_dependency_report_core_vs_custom_r429():
    nodes = [
        _node("KSampler"),  # core
        _node("CheckpointLoaderSimple"),  # core + model loader
        _node("MyCustomSampler"),  # custom
        _node("MyCustomSampler"),  # custom (dup → count 2)
        _node("AnotherCustom"),  # custom
    ]
    r = Ci._build_dependency_report(nodes)
    assert r["total_nodes"] == 5
    assert r["custom_node_count"] == 3  # 2 MyCustom + 1 Another
    assert r["core_node_count"] == 2  # 5 - 3
    assert r["custom_node_types_total"] == 2  # two distinct custom types
    cn = {c["class_type"]: c["count"] for c in r["custom_nodes"]}
    assert cn == {"AnotherCustom": 1, "MyCustomSampler": 2}


def test_dependency_report_fold_disguise_stays_custom_r429():
    # a fullwidth 'Ｋ' folds to ASCII 'K' under NFKC — classifying on the
    # SANITIZED label would count this as the core node KSampler and erase it
    # from the custom-node warning. Classifying on the RAW class_type keeps it
    # custom (R86).
    disguised = "ＫSampler"  # fullwidth K + "Sampler"
    assert disguised not in ("KSampler",)  # raw differs from the core name
    nodes = [_node("KSampler"), _node(disguised)]
    r = Ci._build_dependency_report(nodes)
    assert r["custom_node_count"] == 1  # the disguised node stays custom
    assert r["core_node_count"] == 1  # only the real KSampler is core
    # the stored label IS sanitized (folded) for display…
    labels = [c["class_type"] for c in r["custom_nodes"]]
    assert labels == ["KSampler"]  # display label folded, but still counted custom


def test_dependency_report_io_caps_models_r429():
    nodes = [
        _node("LoadImage"),  # input
        _node("SaveImage"),  # output
        _node("KSampler"),  # → image_generation capability
        _node("LatentUpscale"),  # → upscale capability
        _node(
            "CheckpointLoaderSimple", widgets=["sd_xl.safetensors"]
        ),  # whitelist model confidence
        _node("SomeCustomLoader", widgets=["hidden.ckpt", "notamodel"]),  # structural confidence
    ]
    r = Ci._build_dependency_report(nodes)
    assert r["input_nodes"] == ["LoadImage"]
    assert r["output_nodes"] == ["SaveImage"]
    assert set(r["capabilities_detected"]) == {"image_generation", "upscale"}
    by_file = {m["filename"]: m for m in r["models"]}
    assert by_file["sd_xl.safetensors"]["confidence"] == "whitelist"  # core loader
    assert by_file["hidden.ckpt"]["confidence"] == "structural"  # non-loader node
    assert "notamodel" not in by_file  # non-model extension ignored


def test_dependency_report_empty_r429():
    r = Ci._build_dependency_report([])
    assert r["total_nodes"] == 0
    assert r["core_node_count"] == 0
    assert r["custom_node_count"] == 0
    assert r["capabilities_detected"] == []
    assert r["models"] == []
