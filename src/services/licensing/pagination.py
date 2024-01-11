from typing import Tuple, List, Any

from fastapi_pagination.links import Page
from fastapi_pagination.utils import verify_params

from pydantic import Field

from services.licensing import settings

CustomPage = Page.with_custom_options(
    size=Field(
        settings.pagination_default_pagesize,
        ge=settings.pagination_min_pagesize,
        le=settings.pagination_max_pagesize,
    ),
)


def paginate(items: List[Any], page: int, page_size: int, total: int):
    """simple wrapper to apply pagination"""
    return CustomPage(
        items=items,
        page=page,
        size=max(len(items), 1),
        total=total,
        pages=total / page_size if not total % page_size else total / page_size + 1,
    )


def get_pagination_parameters() -> Tuple[int, int]:
    """
    magic function that extracts page parameters from a
    'paginated' route function.
    :return the selected 'page number' and 'page_size'.
    """
    params, _ = verify_params(None, "limit-offset")
    return params.page, params.size
