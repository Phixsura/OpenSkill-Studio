from app.services.app_marketplace_extension_undo_redo import UndoRedoEngine, UndoableCommand


def _set_cmd(key, value):
    return UndoableCommand(
        name=f"set {key}={value}",
        execute_fn=lambda s: {**s, key: value},
        undo_fn=lambda s: {k: v for k, v in s.items() if k != key})


def _delete_cmd(key):
    return UndoableCommand(
        name=f"delete {key}",
        execute_fn=lambda s: {k: v for k, v in s.items() if k != key},
        undo_fn=lambda s: s)


def test_execute():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("name", "Alice"))
    assert engine.state == {"name": "Alice"}


def test_undo():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("x", 1))
    engine.execute(_set_cmd("y", 2))
    engine.undo()
    assert engine.state == {"x": 1}  # y removed


def test_redo():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("x", 1))
    engine.undo()
    assert engine.state == {}
    engine.redo()
    assert engine.state == {"x": 1}


def test_redo_cleared_on_new_action():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("x", 1))
    engine.undo()
    engine.execute(_set_cmd("y", 2))  # new action clears redo
    result = engine.redo()
    assert result is None  # nothing to redo


def test_multiple_undo():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("a", 1))
    engine.execute(_set_cmd("b", 2))
    engine.execute(_set_cmd("c", 3))
    engine.undo_n(2)
    assert engine.state == {"a": 1}


def test_checkpoint():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("x", 1))
    engine.save_checkpoint("v1")
    engine.execute(_set_cmd("x", 999))
    engine.restore_checkpoint("v1")
    assert engine.state == {"x": 1}


def test_checkpoint_is_undoable():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("x", 1))
    engine.save_checkpoint("v1")
    engine.execute(_set_cmd("x", 2))
    engine.restore_checkpoint("v1")
    engine.undo()  # undo the restore
    assert engine.state == {"x": 2}


def test_can_undo_redo():
    engine = UndoRedoEngine()
    assert engine.can_undo() is False
    engine.execute(_set_cmd("x", 1))
    assert engine.can_undo() is True
    assert engine.can_redo() is False
    engine.undo()
    assert engine.can_redo() is True


def test_history():
    engine = UndoRedoEngine()
    engine.execute(_set_cmd("a", 1))
    engine.execute(_set_cmd("b", 2))
    assert engine.history() == ["set a=1", "set b=2"]


def test_max_history():
    engine = UndoRedoEngine(max_history=3)
    for i in range(10):
        engine.execute(_set_cmd(f"k{i}", i))
    assert len(engine._undo_stack) == 3
