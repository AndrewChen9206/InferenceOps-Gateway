import time

from app.core.timing import elapsed_ms, start_timer


def test_elapsed_ms_returns_positive_integer() -> None:
    started_at = start_timer()

    time.sleep(0.001)

    result = elapsed_ms(started_at)

    assert isinstance(result, int)
    assert result >= 1
