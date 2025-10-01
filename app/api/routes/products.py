from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db import get_session
from app.modules.product.schemas import ProductOut, ProductPage, PaginationMeta
from app.modules.product.service import list_products, SortField, SortOrder

router = APIRouter(tags=["products"])


@router.get("/products", response_model=ProductPage)
async def get_products(
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=200, description="Items per page")] = 20,
    q: Annotated[str | None, Query(description="Search by name (case-insensitive)")] = None,
    sort: Annotated[SortField, Query(description="Sort field")] = "name",  # Literal["name","price"]
    order: Annotated[
        SortOrder, Query(description="Sort direction")
    ] = "asc",  # Literal["asc","desc"]
    session: AsyncSession = Depends(get_session),
):
    items, total, page, pages = await list_products(
        session,
        page=page,
        page_size=page_size,
        q=q,
        sort=sort,
        order=order,
    )

    return ProductPage(
        data=[ProductOut.model_validate(i) for i in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, pages=pages),
    )
