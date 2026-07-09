from decimal import Decimal

from app.core.budget import is_within_daily_budget


def test_budget_allows_request_within_limit() -> None:
    allowed = is_within_daily_budget(
        current_spend_usd=Decimal("0.01"),
        request_cost_usd=Decimal("0.02"),
        daily_budget_usd=Decimal("0.10"),
    )

    assert allowed is True


def test_budget_rejects_request_over_limit() -> None:
    allowed = is_within_daily_budget(
        current_spend_usd=Decimal("0.09"),
        request_cost_usd=Decimal("0.02"),
        daily_budget_usd=Decimal("0.10"),
    )

    assert allowed is False
