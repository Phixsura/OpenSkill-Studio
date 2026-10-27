from app.services.app_marketplace_extension_content_negotiator import ContentNegotiatorService


def test_parse_simple():
    cn = ContentNegotiatorService()
    ranges = cn.parse_accept("application/json")
    assert len(ranges) == 1
    assert ranges[0].full_type == "application/json"
    assert ranges[0].quality == 1.0


def test_parse_with_quality():
    cn = ContentNegotiatorService()
    ranges = cn.parse_accept("text/html;q=0.9, application/json;q=1.0")
    assert ranges[0].full_type == "application/json"  # higher q
    assert ranges[1].full_type == "text/html"


def test_negotiate_exact():
    cn = ContentNegotiatorService()
    result = cn.negotiate("application/json",
                          ["application/json", "text/html"])
    assert result == "application/json"


def test_negotiate_wildcard():
    cn = ContentNegotiatorService()
    result = cn.negotiate("*/*", ["application/json", "text/html"])
    assert result in ("application/json", "text/html")


def test_negotiate_partial_wildcard():
    cn = ContentNegotiatorService()
    result = cn.negotiate("application/*",
                          ["application/json", "text/html"])
    assert result == "application/json"


def test_negotiate_quality_preference():
    cn = ContentNegotiatorService()
    result = cn.negotiate("text/html;q=0.5, application/json;q=1.0",
                          ["text/html", "application/json"])
    assert result == "application/json"


def test_negotiate_406():
    cn = ContentNegotiatorService()
    result = cn.negotiate("application/xml",
                          ["application/json", "text/html"])
    assert result is None  # 406 Not Acceptable


def test_empty_accept():
    cn = ContentNegotiatorService()
    result = cn.negotiate("", ["application/json"])
    assert result == "application/json"  # */* default


def test_language_exact():
    cn = ContentNegotiatorService()
    result = cn.negotiate_language("en-US,en;q=0.9,fr;q=0.8",
                                   ["en", "fr", "de"])
    assert result == "en"


def test_language_prefix():
    cn = ContentNegotiatorService()
    result = cn.negotiate_language("zh", ["zh-CN", "zh-TW", "en"])
    assert result == "zh-CN"


def test_language_fallback():
    cn = ContentNegotiatorService()
    result = cn.negotiate_language("ja", ["en", "fr"])
    assert result == "en"  # first available as fallback


def test_quality_zero_excluded():
    cn = ContentNegotiatorService()
    ranges = cn.parse_accept("text/html, application/json;q=0")
    result = cn.negotiate("text/html, application/json;q=0",
                          ["application/json", "text/html"])
    assert result == "text/html"  # json excluded (q=0)
