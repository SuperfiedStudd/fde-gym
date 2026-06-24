def calculate_review_fee(amount_cents: int) -> int:
    """Return the configured manual-review fee in cents."""
    if amount_cents < 0:
        raise ValueError("amount_cents must be nonnegative")
    if amount_cents == 0:
        return 0
    if amount_cents <= 100_000:
        return 500
    return min(round(amount_cents * 0.01), 25_000)
