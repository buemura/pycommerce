from decimal import Decimal
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.modules.order.model import Order, OrderItem, OrderStatus
from app.modules.order.schemas import (
    OrderItemOut,
    OrderOut,
    OrderPage,
    PaginationMeta,
)
from app.modules.product.model import Product


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _build_order_out(self, order: Order) -> OrderOut:
        return OrderOut(
            id=order.id,
            status=order.status,
            subtotal=float(order.subtotal),
            items=[
                OrderItemOut(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                    line_total=float(item.unit_price) * item.quantity,
                )
                for item in order.items
            ],
        )

    async def get_order(self, order_id: int, user_id: str) -> OrderOut | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(selectinload(Order.items))
        )

        result = await self.session.execute(stmt)
        order = result.scalar_one()
        return self._build_order_out(order) if order else None

    async def list_orders(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> OrderPage:
        count_stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
        total = (await self.session.execute(count_stmt)).scalar_one()

        pages = max(1, ceil(total / page_size)) if total else 1
        page = max(1, min(page, pages))

        orders: list[OrderOut] = []
        if total:
            stmt = (
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.id.desc())
                .limit(page_size)
                .offset((page - 1) * page_size)
                .options(selectinload(Order.items))
            )
            orders = [
                self._build_order_out(order)
                for order in (await self.session.execute(stmt)).scalars().all()
            ]

        return OrderPage(
            data=orders,
            meta=PaginationMeta(page=page, page_size=page_size, total=total, pages=pages),
        )

    async def create_order(
        self,
        user_id: str,
        items: list[tuple[int, int]],
        decrement_stock: bool = True,
    ) -> OrderOut:
        product_ids = [pid for pid, _ in items]
        products = (
            (await self.session.execute(select(Product).where(Product.id.in_(product_ids))))
            .scalars()
            .all()
        )
        prod_map = {p.id: p for p in products}

        for pid, qty in items:
            p = prod_map.get(pid)
            if not p:
                raise ValueError(f"Product {pid} not found")
            if decrement_stock and (p.stock or 0) < qty:
                raise ValueError(f"Insufficient stock for product {p.name} (id={pid})")

        order = Order(user_id=user_id, status=OrderStatus.WAITING_PAYMENT)
        self.session.add(order)
        await self.session.flush()  # get order.id

        subtotal = 0.0
        for pid, qty in items:
            p = prod_map[pid]
            price = float(p.price)
            self.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=p.id,
                    quantity=qty,
                    unit_price=price,
                )
            )
            subtotal += price * qty

        order.subtotal = Decimal(str(round(subtotal, 2)))

        result = await self.get_order(order.id, user_id=user_id)
        if result is None:
            raise ValueError("Order not found after creation")

        return result

    async def update_order_status(
        self,
        user_id: str,
        order_id: int,
        status: OrderStatus,
    ) -> OrderOut:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(selectinload(Order.items))
        )

        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not found")

        if order.status in (OrderStatus.CANCELED, OrderStatus.COMPLETED):
            raise ValueError(f"Order already {order.status}, cannot change status")

        # apply change
        order.status = status

        # persist without closing the outer transaction
        await self.session.flush()

        # pull server-side updates (e.g., updated_at onupdate=func.now())
        await self.session.refresh(order)

        return self._build_order_out(order)
