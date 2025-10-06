from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.di_container import make_order_client
from app.shared.db import get_session, get_transaction_session
from app.api.deps import get_current_user
from app.modules.order.schemas import (
    OrderCreateIn,
    OrderOut,
    OrderPage,
    OrderStatusUpdate,
)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderPage)
async def list_my_orders(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    client = make_order_client(session)
    return await client.list_orders(user_id=user.id, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderOut)
async def get_my_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    client = make_order_client(session)
    return await client.get_order(user_id=user.id, order_id=order_id)


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreateIn,
    session: AsyncSession = Depends(get_transaction_session),
    user=Depends(get_current_user),
):
    client = make_order_client(session)
    items = [(item.product_id, item.quantity) for item in payload.items]
    return await client.create_order(user_id=user.id, items=items, decrement_stock=True)


@router.patch("/{order_id}/status", response_model=OrderOut)
async def set_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    session: AsyncSession = Depends(get_transaction_session),
    user=Depends(get_current_user),
):
    client = make_order_client(session)
    return await client.update_order_status(
        user_id=user.id, order_id=order_id, status=payload.status
    )
