import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects import postgresql

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.domain.filters import apply_status_filter
from app.models import Claim


def test_status_filter_targets_status_column() -> None:
    query = apply_status_filter(select(Claim), "submitted")
    sql = str(query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    assert "claims.status = 'submitted'" in sql
    assert "claimant_name = 'submitted'" not in sql


def test_missing_status_does_not_add_predicate() -> None:
    sql = str(apply_status_filter(select(Claim), None))
    assert " WHERE " not in sql.upper()

