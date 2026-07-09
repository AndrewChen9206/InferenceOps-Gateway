from decimal import Decimal


def is_within_daily_budget(
    *,
    current_spend_usd: Decimal,
    request_cost_usd: Decimal,
    daily_budget_usd: Decimal,
) -> bool:
    projected_spend = current_spend_usd + request_cost_usd
    return projected_spend <= daily_budget_usd
