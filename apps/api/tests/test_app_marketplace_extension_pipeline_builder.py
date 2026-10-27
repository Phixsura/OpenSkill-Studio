from app.services.app_marketplace_extension_pipeline_builder import PipelineBuilderService


def test_simple_pipeline():
    svc = PipelineBuilderService()
    spec = (svc.create("etl")
            .source("gen", lambda: range(10))
            .map("double", lambda x: x * 2)
            .filter("even", lambda x: x % 4 == 0)
            .build())
    result = svc.execute(spec=spec)
    assert result["status"] == "completed"
    assert result["output"] == [0, 4, 8, 12, 16]


def test_flat_map():
    svc = PipelineBuilderService()
    spec = (svc.create("split")
            .source("gen", lambda: ["hello world", "foo bar"])
            .flat_map("words", lambda s: s.split())
            .build())
    result = svc.execute(spec=spec)
    assert result["output"] == ["hello", "world", "foo", "bar"]


def test_reduce():
    svc = PipelineBuilderService()
    spec = (svc.create("sum")
            .source("gen", lambda: range(1, 6))
            .reduce("total", lambda acc, x: acc + x, initial=0)
            .build())
    result = svc.execute(spec=spec)
    assert result["output"] == [15]


def test_sink():
    svc = PipelineBuilderService()
    collected = []
    spec = (svc.create("collect")
            .source("gen", lambda: [1, 2, 3])
            .sink("store", lambda x: collected.append(x))
            .build())
    svc.execute(spec=spec)
    assert collected == [1, 2, 3]


def test_error_handler():
    svc = PipelineBuilderService()
    spec = (svc.create("safe")
            .source("gen", lambda: [1, 0, 3])
            .map("divide", lambda x: 10 // x,
                 on_error=lambda item, err: -1)
            .build())
    result = svc.execute(spec=spec)
    assert result["output"] == [10, -1, 3]  # 0 → error → -1


def test_validation_no_source():
    svc = PipelineBuilderService()
    try:
        svc.create("bad").map("m", lambda x: x).build()
        assert False
    except ValueError:
        pass


def test_validation_duplicate_names():
    svc = PipelineBuilderService()
    try:
        (svc.create("bad")
         .source("step", lambda: [])
         .map("step", lambda x: x)  # duplicate name
         .build())
        assert False
    except ValueError:
        pass


def test_register_and_execute():
    svc = PipelineBuilderService()
    spec = (svc.create("registered")
            .source("gen", lambda: [1, 2, 3])
            .map("inc", lambda x: x + 1)
            .build())
    svc.register(spec)
    result = svc.execute("registered")
    assert result["output"] == [2, 3, 4]


def test_chained_operations():
    svc = PipelineBuilderService()
    spec = (svc.create("chain")
            .source("gen", lambda: range(20))
            .filter("gt5", lambda x: x > 5)
            .map("square", lambda x: x ** 2)
            .filter("lt200", lambda x: x < 200)
            .build())
    result = svc.execute(spec=spec)
    assert all(v < 200 for v in result["output"])
    assert all(v > 25 for v in result["output"])


def test_dry_run():
    svc = PipelineBuilderService()
    spec = (svc.create("big")
            .source("gen", lambda: range(1000))
            .map("inc", lambda x: x + 1)
            .build())
    result = svc.dry_run(spec, sample_size=3)
    assert result["dry_run"] is True
    assert result["output_count"] == 3
