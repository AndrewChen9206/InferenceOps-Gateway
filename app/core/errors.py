class GatewayError(Exception):
    pass


class UnknownUserError(GatewayError):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"Unknown user_id: {user_id}")


class ModelPriceNotFoundError(GatewayError):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        super().__init__(f"Missing model price for model: {model_name}")


class RateLimitExceededError(GatewayError):
    def __init__(self, user_id: str, limit: int) -> None:
        self.user_id = user_id
        self.limit = limit
        super().__init__(
            f"Rate limit exceeded for user '{user_id}'. Limit: {limit} requests per minute."
        )


class BudgetExceededError(GatewayError):
    def __init__(self, user_id: str, budget_usd: str, projected_spend_usd: str) -> None:
        self.user_id = user_id
        self.budget_usd = budget_usd
        self.projected_spend_usd = projected_spend_usd
        super().__init__(
            f"Daily budget exceeded for user '{user_id}'. "
            f"Budget: ${budget_usd}, projected spend: ${projected_spend_usd}."
        )
