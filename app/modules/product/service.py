from math import ceil
from typing import Literal, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.modules.product.model import Product

SortField = Literal["name", "price"]
SortOrder = Literal["asc", "desc"]


def _apply_filters_sort(
    stmt: Select,
    q: str | None,
    sort: SortField,
    order: SortOrder,
) -> Select:
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q}%"))
    sort_col = Product.name if sort == "name" else Product.price
    stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc(), Product.id.asc())
    return stmt


async def list_products(
    session: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    sort: SortField = "name",
    order: SortOrder = "asc",
) -> Tuple[list[Product], int, int, int]:
    # count
    count_stmt = select(func.count()).select_from(Product)
    if q:
        count_stmt = count_stmt.where(Product.name.ilike(f"%{q}%"))
    total = (await session.execute(count_stmt)).scalar_one()

    pages = max(1, ceil(total / page_size)) if total else 1
    page = max(1, min(page, pages))  # clamp

    # page query
    stmt = select(Product)
    stmt = _apply_filters_sort(stmt, q, sort, order)
    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    rows = list((await session.execute(stmt)).scalars().all())
    return rows, total, page, pages
