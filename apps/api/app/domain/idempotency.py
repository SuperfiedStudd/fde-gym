from typing import Any


def request_fingerprint(payload: dict[str, Any]) -> str:
    # MISSION_BUG(lv2-claim-idempotency): repr is ordering-dependent and not a stable fingerprint.
    return repr(payload)
