import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/api").resolve()))
from app.domain.pagination import pagination_window


def test_pagination_window_uses_one_based_pages() -> None:
    assert pagination_window(1, 25) == (0, 25)
    assert pagination_window(3, 10) == (20, 10)

