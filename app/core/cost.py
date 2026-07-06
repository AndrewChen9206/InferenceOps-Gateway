from decimal import Decimal


def estimate_input_tokens(prompt: str) -> int:
    return max(1, len(prompt) // 4)


def estimate_output_tokens(max_tokens: int) -> int:
    return max(1, max_tokens // 4)


def estimate_cost_usd(
    *,
    input_tokens: int,
    output_tokens: int,
    input_cost_per_1k_tokens: Decimal,
    output_cost_per_1k_tokens: Decimal,
) -> Decimal:
    input_cost = Decimal(input_tokens) / Decimal(1000) * input_cost_per_1k_tokens
    output_cost = Decimal(output_tokens) / Decimal(1000) * output_cost_per_1k_tokens
    return input_cost + output_cost
