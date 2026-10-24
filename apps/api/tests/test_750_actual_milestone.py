"""750 actual commits milestone."""
import os

def test_services():
    d = os.path.join(os.path.dirname(__file__), "..", "app", "services")
    n = len([f for f in os.listdir(d) if f.endswith(".py") and f != "__init__.py"])
    assert n >= 170, f"{n} services"
