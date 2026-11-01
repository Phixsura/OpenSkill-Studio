from app.services.app_marketplace_extension_cron_parser import CronParserService
import pytest


def test_every_minute():
    cp = CronParserService()
    fields = cp.parse("* * * * *")
    assert fields[0].values == set(range(0, 60))


def test_specific_time():
    cp = CronParserService()
    assert cp.matches("30 9 * * *", minute=30, hour=9, day=15, month=6, dow=1) is True
    assert cp.matches("30 9 * * *", minute=0, hour=9, day=15, month=6, dow=1) is False


def test_step():
    cp = CronParserService()
    fields = cp.parse("*/15 * * * *")
    assert fields[0].values == {0, 15, 30, 45}


def test_range():
    cp = CronParserService()
    fields = cp.parse("* 9-17 * * *")
    assert fields[1].values == set(range(9, 18))


def test_list():
    cp = CronParserService()
    fields = cp.parse("0 8,12,18 * * *")
    assert fields[1].values == {8, 12, 18}


def test_dow():
    cp = CronParserService()
    assert cp.matches("0 9 * * 1-5", minute=0, hour=9, day=1, month=1, dow=3) is True  # Wed
    assert cp.matches("0 9 * * 1-5", minute=0, hour=9, day=1, month=1, dow=0) is False  # Sun


def test_combined():
    cp = CronParserService()
    # Every 5 minutes during work hours on weekdays
    fields = cp.parse("*/5 9-17 * * 1-5")
    assert 0 in fields[0].values
    assert 5 in fields[0].values
    assert 9 in fields[1].values
    assert 1 in fields[4].values
    assert 0 not in fields[4].values


def test_month_names():
    cp = CronParserService()
    fields = cp.parse("0 0 1 jan,jun *")
    assert fields[3].values == {1, 6}


def test_dow_names():
    cp = CronParserService()
    fields = cp.parse("0 0 * * mon,wed,fri")
    assert fields[4].values == {1, 3, 5}


def test_invalid_field_count():
    cp = CronParserService()
    with pytest.raises(ValueError):
        cp.parse("* * *")


def test_out_of_range():
    cp = CronParserService()
    with pytest.raises(ValueError):
        cp.parse("60 * * * *")  # minute max is 59


def test_describe():
    cp = CronParserService()
    desc = cp.describe("30 9 * * 1-5")
    assert "30" in desc
    assert "9" in desc
    assert "Mon" in desc


def test_expanded():
    cp = CronParserService()
    expanded = cp.get_expanded("0,30 */6 1,15 * *")
    assert expanded["minute"] == [0, 30]
    assert expanded["hour"] == [0, 6, 12, 18]
    assert expanded["day_of_month"] == [1, 15]
