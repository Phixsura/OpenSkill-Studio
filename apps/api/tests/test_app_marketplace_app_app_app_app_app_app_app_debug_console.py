from app.services.app_marketplace_app_app_app_app_app_app_app_debug_console import (
    add_breakpoint, log_output, get_console, clear_console,
)

def test_breakpoint():
    clear_console()
    bp = add_breakpoint("app.py", 42, "x > 10")
    assert bp["id"] == 1
    assert bp["line"] == 42
    clear_console()

def test_console():
    clear_console()
    log_output("info", "Server started", "main")
    log_output("error", "Connection failed", "db")
    log_output("info", "Request handled", "api")
    r = get_console()
    assert r["total"] == 3
    assert r["by_level"]["info"] == 2
    assert r["by_level"]["error"] == 1
    r2 = get_console(level="error")
    assert r2["shown"] == 1
    clear_console()
