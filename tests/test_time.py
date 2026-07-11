from datetime import UTC, datetime, timedelta, timezone

from app.core.time import start_of_utc_day, to_naive_utc, utc_now


def test_utc_now_returns_naive_datetime() -> None:
    value = utc_now()

    assert value.tzinfo is None


def test_to_naive_utc_keeps_naive_datetime_unchanged() -> None:
    value = datetime(2026, 7, 11, 8, 30)

    result = to_naive_utc(value)

    assert result == value
    assert result.tzinfo is None


def test_to_naive_utc_converts_aware_datetime_to_utc() -> None:
    taipei_timezone = timezone(timedelta(hours=8))
    value = datetime(2026, 7, 11, 16, 30, tzinfo=taipei_timezone)

    result = to_naive_utc(value)

    assert result == datetime(2026, 7, 11, 8, 30)
    assert result.tzinfo is None


def test_start_of_utc_day_for_aware_datetime() -> None:
    value = datetime(2026, 7, 11, 16, 30, tzinfo=UTC)

    result = start_of_utc_day(value)

    assert result == datetime(2026, 7, 11, 0, 0)


def test_start_of_utc_day_converts_timezone_before_getting_date() -> None:
    taipei_timezone = timezone(timedelta(hours=8))
    value = datetime(2026, 7, 11, 3, 0, tzinfo=taipei_timezone)

    result = start_of_utc_day(value)

    assert result == datetime(2026, 7, 10, 0, 0)
