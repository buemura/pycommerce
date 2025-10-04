from abc import ABC, abstractmethod

from app.modules.order.model import Order, OrderStatus
from app.modules.order.schemas import OrderPage
from app.modules.order.service import OrderService


class OrderClientInterface(ABC):
    @abstractmethod
    async def get_order(self, order_id: int, user_id: int) -> Order | None:
        pass

    @abstractmethod
    async def list_orders(self, user_id: int, page: int, page_size: int) -> OrderPage:
        pass

    @abstractmethod
    async def create_order(
        self, user_id: int, items: list[tuple[int, int]], decrement_stock: bool
    ) -> Order:
        pass

    @abstractmethod
    async def update_order_status(self, user_id: int, order_id: int, status: OrderStatus) -> Order:
        pass


class OrderClient(OrderClientInterface):
    def __init__(self, db_session):
        self.order_service = OrderService(session=db_session)

    async def get_order(self, order_id: int, user_id: int) -> Order | None:
        return await self.order_service.get_order(order_id, user_id=user_id)

    async def list_orders(self, user_id: int, page: int, page_size: int) -> OrderPage:
        return await self.order_service.list_orders(user_id, page, page_size)

    async def create_order(
        self, user_id: int, items: list[tuple[int, int]], decrement_stock: bool
    ) -> Order:
        return await self.order_service.create_order(
            user_id, items=items, decrement_stock=decrement_stock
        )

    async def update_order_status(self, user_id: int, order_id: int, status: OrderStatus) -> Order:
        return await self.order_service.update_order_status(user_id, order_id, status)
