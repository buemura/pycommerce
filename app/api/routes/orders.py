from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db import get_session, get_transaction_session
from app.api.deps import get_current_user
from app.modules.order.schemas import (
    OrderCreateIn,
    OrderOut,
    OrderItemOut,
    OrderPage,
    PaginationMeta,
    OrderStatusUpdate,
)
from app.modules.order.service import (
    create_order_for_user,
    get_order,
    list_orders,
    update_order_status,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderPage)
async def list_my_orders(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    rows, total, page, pages = await list_orders(
        session, user_id=user.id, page=page, page_size=page_size
    )
    items = [
        OrderOut(
            id=o.id,
            status=o.status,
            subtotal=o.subtotal,
            items=[OrderItemOut.from_orm_item(oi) for oi in o.items],
        )
        for o in rows
    ]
    return OrderPage(
        data=items,
        meta=PaginationMeta(page=page, page_size=page_size, total=total, pages=pages),
    )


@router.get("/{order_id}", response_model=OrderOut)
async def get_my_order(
    order_id: int, session: AsyncSession = Depends(get_session), user=Depends(get_current_user)
):
    order = await get_order(session, order_id, user_id=user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=order.subtotal,
        items=[OrderItemOut.from_orm_item(oi) for oi in order.items],
    )


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreateIn,
    session: AsyncSession = Depends(get_transaction_session),
    user=Depends(get_current_user),
):
    try:
        items_tuples = [(it.product_id, it.quantity) for it in payload.items]
        order = await create_order_for_user(session, user_id=user.id, items=items_tuples)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=order.subtotal,
        items=[OrderItemOut.from_orm_item(oi) for oi in order.items],
    )


@router.patch("/{order_id}/status", response_model=OrderOut)
async def set_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    session: AsyncSession = Depends(get_transaction_session),
    user=Depends(get_current_user),
):
    try:
        order = await update_order_status(
            session, user_id=user.id, order_id=order_id, status=payload.status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=order.subtotal,
        items=[OrderItemOut.from_orm_item(oi) for oi in order.items],
    )
