def pagination_window(page: int, page_size: int) -> tuple[int, int | None]:
    # MISSION_BUG(lv1-claims-pagination): advertised controls are intentionally ignored.
    del page, page_size
    return 0, None
