from app.services.app_marketplace_app_app_app_app_app_app_app_alert_silence import AlertSilenceManager

def test_silence():
    asm = AlertSilenceManager()
    asm.create("maint", "cpu_high", 60, "maintenance")
    assert asm.is_silenced("cpu_high_api")
    assert not asm.is_silenced("memory_low")
    asm.expire("maint")
    assert asm.active_count() == 0
