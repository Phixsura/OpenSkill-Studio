from app.services.app_marketplace_extension_db_connector import ExtDbConnectorService

def test_connect():
    svc = ExtDbConnectorService()
    conn = svc.connect("ext-1", "postgres", "localhost", 5432, "mydb")
    assert conn.status == "connected"
    assert conn.pool_size == 5

def test_query_and_release():
    svc = ExtDbConnectorService()
    conn = svc.connect("ext-1", "redis", "localhost", 6379, "0", pool_size=2)
    assert svc.query(conn.conn_id) is True
    assert svc.query(conn.conn_id) is True
    assert svc.query(conn.conn_id) is False  # pool exhausted
    svc.release(conn.conn_id)
    assert svc.query(conn.conn_id) is True

def test_disconnect():
    svc = ExtDbConnectorService()
    conn = svc.connect("ext-1", "mysql", "localhost", 3306, "app")
    svc.disconnect(conn.conn_id)
    assert svc.query(conn.conn_id) is False

def test_unsupported_db():
    svc = ExtDbConnectorService()
    try:
        svc.connect("ext-1", "oracle", "localhost", 1521, "xe")
        assert False
    except ValueError:
        pass
