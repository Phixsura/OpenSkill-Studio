from app.services.app_marketplace_extension_data_pipeline import (
    DataPipelineService, PipelineRecord
)


def _make_records(n):
    return [PipelineRecord(f"r{i}", {"value": i}) for i in range(n)]


def test_source_to_sink():
    pipe = DataPipelineService()
    collected = []
    pipe.add_source("gen", lambda: _make_records(5))
    pipe.add_sink("store", lambda r: collected.append(r))
    result = pipe.run()
    assert result["status"] == "completed"
    assert result["processed"] == 5
    assert len(collected) == 5


def test_transform():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(3))
    pipe.add_transform("double", lambda r: PipelineRecord(
        r.record_id, {"value": r.data["value"] * 2}))
    collected = []
    pipe.add_sink("store", lambda r: collected.append(r))
    pipe.run()
    assert collected[0].data["value"] == 0
    assert collected[1].data["value"] == 2
    assert collected[2].data["value"] == 4


def test_filter():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(10))
    pipe.add_filter("evens", lambda r: r.data["value"] % 2 == 0)
    collected = []
    pipe.add_sink("store", lambda r: collected.append(r))
    pipe.run()
    assert len(collected) == 5  # 0,2,4,6,8


def test_chained_stages():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(20))
    pipe.add_filter("gt5", lambda r: r.data["value"] > 5)
    pipe.add_transform("square", lambda r: PipelineRecord(
        r.record_id, {"value": r.data["value"] ** 2}))
    pipe.add_filter("lt200", lambda r: r.data["value"] < 200)
    collected = []
    pipe.add_sink("store", lambda r: collected.append(r))
    pipe.run()
    # Values > 5, squared, < 200: 6²=36, 7²=49, ..., 13²=169, 14²=196
    assert all(c.data["value"] < 200 for c in collected)
    assert all(c.data["value"] > 25 for c in collected)


def test_dead_letter_on_error():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(5))
    pipe.add_transform("risky", lambda r: (_ for _ in ()).throw(
        ValueError("bad")) if r.data["value"] == 3 else r)
    collected = []
    pipe.add_sink("store", lambda r: collected.append(r))
    result = pipe.run()
    assert len(collected) == 4  # 0,1,2,4 (3 went to dead letter)
    assert result["dead_letters"] == 1


def test_dead_letter_details():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(3))
    pipe.add_transform("fail", lambda r: (_ for _ in ()).throw(
        RuntimeError("crash")) if r.data["value"] == 1 else r)
    pipe.add_sink("store", lambda r: None)
    pipe.run()
    dl = pipe.get_dead_letters()
    assert len(dl) == 1
    assert dl[0]["stage"] == "fail"
    assert "crash" in dl[0]["error"]


def test_max_records():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(100))
    collected = []
    pipe.add_sink("store", lambda r: collected.append(r))
    pipe.run(max_records=10)
    assert len(collected) == 10


def test_metrics():
    pipe = DataPipelineService()
    pipe.add_source("gen", lambda: _make_records(10))
    pipe.add_filter("half", lambda r: r.data["value"] < 5)
    pipe.add_sink("store", lambda r: None)
    pipe.run()
    metrics = pipe.get_metrics()
    assert metrics[1]["in"] == 10
    assert metrics[1]["out"] == 5
    assert metrics[2]["in"] == 5


def test_checkpoint():
    pipe = DataPipelineService()
    pipe.save_checkpoint({"last_offset": 42})
    cp = pipe.get_checkpoint()
    assert cp["data"]["last_offset"] == 42
