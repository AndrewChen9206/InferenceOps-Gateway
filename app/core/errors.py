class GatewayError(Exception):
    pass


class RateLimitExceededError(GatewayError):
    def __init__(self, user_id: str, limit: int) -> None:
        self.user_id = user_id
        self.limit = limit
        super().__init__(
            f"Rate limit exceeded for user '{user_id}'. Limit: {limit} requests per minute."
        )
