from sqlalchemy import Select

from app.models import Claim


def apply_status_filter(query: Select, status_filter: str | None) -> Select:
    if not status_filter:
        return query
    # MISSION_BUG(lv1-sql-status-filter): predicate points to the wrong column.
    return query.where(Claim.claimant_name == status_filter)
