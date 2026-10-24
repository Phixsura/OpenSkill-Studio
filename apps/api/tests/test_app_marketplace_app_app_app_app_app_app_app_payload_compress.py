from app.services.app_marketplace_app_app_app_app_app_app_app_payload_compress import compress, decompress, should_compress

def test_compress_decompress():
    data = '{"key": "value", "items": [1, 2, 3, 4, 5]}' * 10
    c = compress(data)
    assert c["ratio_pct"] > 0
    d = decompress(c["encoded"])
    assert d["data"] == data

def test_should_compress():
    assert should_compress(2000, "application/json")["should_compress"]
    assert not should_compress(500, "application/json")["should_compress"]
    assert not should_compress(2000, "image/png")["should_compress"]
