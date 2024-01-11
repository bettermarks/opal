from typing import Any

from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def execute_paginated_query(
    session: AsyncSession, stmt: Select, page: int, page_size: int
) -> Any:
    total = (await session.execute(select(func.count()).select_from(stmt))).scalar()
    items = (
        (await session.execute(stmt.offset((page - 1) * page_size).limit(page_size)))
        .scalars()
        .all()
    )
    return items, total
