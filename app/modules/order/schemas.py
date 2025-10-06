from __future__ import annotations
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Annotated
from pydantic import BaseModel, Field

from .model import OrderStatus


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int


class OrderCreateIn(BaseModel):
    items: List[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: Annotated[float, Field(ge=0)]
    line_total: Annotated[float, Field(ge=0)]


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    subtotal: Annotated[float, Field(ge=0)]
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class OrderPage(BaseModel):
    data: list[OrderOut]
    meta: PaginationMeta


# ----- Status update -----
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
