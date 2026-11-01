from app.services.app_marketplace_extension_expr_eval import ExprEvaluatorService, ExprError
import pytest


def test_arithmetic():
    ev = ExprEvaluatorService()
    assert ev.evaluate("2 + 3") == 5
    assert ev.evaluate("10 - 4") == 6
    assert ev.evaluate("3 * 7") == 21
    assert ev.evaluate("15 / 3") == 5.0
    assert ev.evaluate("17 % 5") == 2


def test_precedence():
    ev = ExprEvaluatorService()
    assert ev.evaluate("2 + 3 * 4") == 14  # not 20
    assert ev.evaluate("(2 + 3) * 4") == 20


def test_power():
    ev = ExprEvaluatorService()
    assert ev.evaluate("2 ** 10") == 1024


def test_unary_minus():
    ev = ExprEvaluatorService()
    assert ev.evaluate("-5 + 3") == -2


def test_comparison():
    ev = ExprEvaluatorService()
    assert ev.evaluate("5 > 3") is True
    assert ev.evaluate("2 == 2") is True
    assert ev.evaluate("1 != 2") is True
    assert ev.evaluate("5 <= 3") is False


def test_logical():
    ev = ExprEvaluatorService()
    assert ev.evaluate("1 > 0 and 2 > 1") is True
    assert ev.evaluate("1 > 0 or 2 < 1") is True
    assert ev.evaluate("not 0") is True


def test_variables():
    ev = ExprEvaluatorService()
    assert ev.evaluate("price * quantity", {"price": 10, "quantity": 5}) == 50
    assert ev.evaluate("score >= threshold", {"score": 85, "threshold": 80}) is True


def test_functions():
    ev = ExprEvaluatorService()
    assert ev.evaluate("max(3, 7, 1)") == 7
    assert ev.evaluate("min(10, 5, 20)") == 5
    assert ev.evaluate("abs(-42)") == 42
    assert ev.evaluate("round(3.14159, 2)") == 3.14


def test_if_function():
    ev = ExprEvaluatorService()
    assert ev.evaluate('if(score > 90, "A", "B")', {"score": 95}) == "A"
    assert ev.evaluate('if(score > 90, "A", "B")', {"score": 80}) == "B"


def test_nested():
    ev = ExprEvaluatorService()
    assert ev.evaluate("max(abs(-5), min(3, 7))") == 5


def test_division_by_zero():
    ev = ExprEvaluatorService()
    with pytest.raises(ExprError, match="Division by zero"):
        ev.evaluate("10 / 0")


def test_unknown_variable():
    ev = ExprEvaluatorService()
    with pytest.raises(ExprError, match="Unknown variable"):
        ev.evaluate("x + 1")
