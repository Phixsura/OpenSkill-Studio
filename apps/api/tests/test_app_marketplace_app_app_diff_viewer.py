from app.services.app_marketplace_app_app_diff_viewer import parse_unified_diff

DIFF = """@@ -1,3 +1,4 @@
 unchanged
-old line
+new line
+added line
 context"""

def test_parse():
    r = parse_unified_diff(diff_text=DIFF)
    assert r["additions"] == 2
    assert r["removals"] == 1
    assert r["total_changes"] == 3
    assert len(r["hunks"]) == 1
    assert len(r["hunks"][0]["lines"]) == 5

def test_xss():
    d = "@@ -1 +1 @@\n+<script>alert(1)</script>"
    r = parse_unified_diff(diff_text=d)
    assert "<script>" not in r["hunks"][0]["lines"][0]["content"]
