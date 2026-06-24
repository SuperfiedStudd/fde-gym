from uuid import UUID


def claim_cache_key(claim_id: UUID) -> str:
    return f"claim:{claim_id}"
