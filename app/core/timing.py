import math
import time


def start_timer() -> float:
    """Return a monotonic high-resolution timer value."""
    return time.perf_counter()


def elapsed_ms(started_at: float) -> int:
    """Return elapsed monotonic time in whole milliseconds."""
    elapsed_seconds = time.perf_counter() - started_at
    return max(1, math.ceil(elapsed_seconds * 1000))
