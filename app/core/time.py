from datetime import UTC, datetime, time


def utc_now() -> datetime:
    """Return the current time as a naive datetime representing UTC."""
    return datetime.now(UTC).replace(tzinfo=None)


def to_naive_utc(value: datetime) -> datetime:
    """Convert an aware datetime to naive UTC.

    A naive input is assumed to already represent UTC.
    """
    if value.tzinfo is None:
        return value

    return value.astimezone(UTC).replace(tzinfo=None)


def start_of_utc_day(value: datetime | None = None) -> datetime:
    """Return 00:00:00 for the UTC day containing the given datetime."""
    current_time = to_naive_utc(value) if value is not None else utc_now()

    return datetime.combine(
        current_time.date(),
        time.min,
    )
