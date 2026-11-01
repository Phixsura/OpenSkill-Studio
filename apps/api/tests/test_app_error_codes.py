import pytest
from app.services.app_error_codes import get_error, list_error_codes, ERROR_CODES

@pytest.mark.parametrize("code", ERROR_CODES.keys())
def test_get_known(code):
    err = get_error(code)
    assert err["code"] == code
    assert 400 <= err["status"] < 500 or err["status"] == 500

def test_get_unknown():
    err = get_error("UNKNOWN_CODE")
    assert err["status"] == 500

def test_list():
    codes = list_error_codes()
    assert len(codes) == len(ERROR_CODES)
    assert codes == sorted(codes)

def test_count():
    assert len(ERROR_CODES) >= 15
