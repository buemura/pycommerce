from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.client import UserClientInterface, UserClient
from app.modules.product.client import ProductClientInterface, ProductClient
from app.modules.order.client import OrderClientInterface, OrderClient


def make_user_client(db_session: AsyncSession) -> UserClientInterface:
    return UserClient(db_session=db_session)


def make_product_client(db_session: AsyncSession) -> ProductClientInterface:
    return ProductClient(db_session=db_session)


def make_order_client(db_session: AsyncSession) -> OrderClientInterface:
    return OrderClient(db_session=db_session)
