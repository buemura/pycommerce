from __future__ import annotations
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Annotated
from pydantic import BaseModel, Field

from .model import OrderStatus


class OrderItemIn(BaseModel):
    product_id: int
    quantity: Annotated[int, Field(ge=1)] = 1  # instead of conint


class OrderCreateIn(BaseModel):
    items: List[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    product_id: int
    unit_price: Annotated[float, Field(ge=0)]
    quantity: int
    line_total: Annotated[float, Field(ge=0)]

    @classmethod
    def from_orm_item(cls, oi) -> "OrderItemOut":
        unit = float(oi.unit_price)
        return cls(
            product_id=oi.product_id,
            unit_price=unit,
            quantity=oi.quantity,
            line_total=unit * oi.quantity,
        )


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
