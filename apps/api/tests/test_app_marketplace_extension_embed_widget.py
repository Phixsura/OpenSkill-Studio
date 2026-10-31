from app.services.app_marketplace_extension_embed_widget import ExtEmbedWidgetService, EmbedConfig

def test_html():
    svc = ExtEmbedWidgetService()
    cfg = EmbedConfig(extension_id="ext-1", theme="dark", size="medium")
    html_out = svc.generate_html(cfg, "Auth Plugin", 4.5, 1200)
    assert "Auth Plugin" in html_out
    assert "osk-dark" in html_out
    assert "1,200 installs" in html_out

def test_iframe():
    svc = ExtEmbedWidgetService()
    cfg = EmbedConfig(extension_id="ext-1", size="large")
    iframe = svc.generate_iframe(cfg)
    assert 'width="400"' in iframe
    assert "ext-1" in iframe

def test_markdown():
    svc = ExtEmbedWidgetService()
    cfg = EmbedConfig(extension_id="ext-1")
    md = svc.generate_markdown(cfg, "Auth Plugin", 4.5)
    assert "**Auth Plugin**" in md
    assert "4.5/5.0" in md
