from app.services.app_marketplace_app_app_app_app_app_app_app_conn_string import build_connection_string

def test_build():
    r = build_connection_string("postgres", "db.example.com", 5432, "mydb",
                                  user="admin", password="s3cret!")
    assert r["built"]
    assert "postgresql://" in r["uri"]
    assert "s3cret" not in r["masked"]
    assert "****" in r["masked"]

def test_params():
    r = build_connection_string("postgres", "localhost", 5432, "db",
                                  params={"sslmode": "require"})
    assert "sslmode=require" in r["uri"]

def test_invalid():
    r = build_connection_string("oracle", "host", 1521, "db")
    assert not r["built"]
