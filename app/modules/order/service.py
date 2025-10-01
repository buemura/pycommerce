from decimal import Decimal
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.modules.order.model import Order, OrderItem, OrderStatus
from app.modules.product.model import Product


async def get_order(session: AsyncSession, order_id: int, *, user_id: int) -> Order | None:
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items))
    )
    return (await session.execute(stmt)).scalars().first()


async def list_orders(
    session: AsyncSession,
    *,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Order], int, int, int]:
    count_stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
    total = (await session.execute(count_stmt)).scalar_one()

    pages = max(1, ceil(total / page_size)) if total else 1
    page = max(1, min(page, pages))

    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
        .options(selectinload(Order.items))
    )
    rows = (await session.execute(stmt)).scalars().all()
    return list(rows), total, page, pages


async def create_order_for_user(
    session: AsyncSession,
    *,
    user_id: int,
    items: list[tuple[int, int]],
    decrement_stock: bool = True,
) -> Order:
    product_ids = [pid for pid, _ in items]
    products = (
        (await session.execute(select(Product).where(Product.id.in_(product_ids)))).scalars().all()
    )
    prod_map = {p.id: p for p in products}

    for pid, qty in items:
        p = prod_map.get(pid)
        if not p:
            raise ValueError(f"Product {pid} not found")
        if decrement_stock and (p.stock or 0) < qty:
            raise ValueError(f"Insufficient stock for product {p.name} (id={pid})")

    order = Order(user_id=user_id, status=OrderStatus.WAITING_PAYMENT)
    session.add(order)
    await session.flush()  # get order.id

    subtotal = 0.0
    for pid, qty in items:
        p = prod_map[pid]
        price = float(p.price)
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=p.id,
                unit_price=price,
                quantity=qty,
            )
        )
        subtotal += price * qty

    order.subtotal = Decimal(str(round(subtotal, 2)))

    result = await get_order(session, order.id, user_id=user_id)
    if result is None:
        raise ValueError("Order not found after creation")
    return result


async def update_order_status(
    session: AsyncSession, *, user_id: int, order_id: int, status: OrderStatus
) -> Order:
    order = await get_order(session, order_id, user_id=user_id)
    if not order:
        raise ValueError("Order not found")
    if order.status in (OrderStatus.CANCELED, OrderStatus.COMPLETED):
        raise ValueError(f"Order already {order.status}, cannot change status")

    order.status = status
    updated_order = await get_order(session, order_id, user_id=user_id)
    if not updated_order:
        raise ValueError("Order not found after status update")
    return updated_order
