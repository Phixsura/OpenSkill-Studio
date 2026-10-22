"""Execution queue tests."""
import pytest
from app.services.app_execution_queue import (
    enqueue_execution, can_execute, start_execution, finish_execution,
    get_queue_depth, get_running_count, DEFAULT_MAX_CONCURRENT,
)

APP = "queue-test"

def test_enqueue():
    e = enqueue_execution(app_id=APP, installation_id="i1", function_name="fn", payload={})
    assert e["status"] == "queued"
    assert e["app_id"] == APP

def test_can_execute():
    assert can_execute("fresh-app") is True

def test_concurrency_limit():
    app = "limit-test"
    for _ in range(DEFAULT_MAX_CONCURRENT):
        start_execution(app)
    assert can_execute(app) is False
    finish_execution(app)
    assert can_execute(app) is True

def test_running_count():
    app = "count-test"
    start_execution(app)
    start_execution(app)
    assert get_running_count(app) == 2
    finish_execution(app)
    assert get_running_count(app) == 1

def test_queue_depth():
    app = "depth-test"
    enqueue_execution(app_id=app, installation_id="i1", function_name="f", payload={})
    assert get_queue_depth(app) >= 1

def test_finish_never_negative():
    app = "neg-test"
    finish_execution(app)
    finish_execution(app)
    assert get_running_count(app) == 0
