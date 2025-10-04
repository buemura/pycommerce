from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.schemas import ProductPage
from app.modules.product.service import ProductService, SortField, SortOrder


class ProductClientInterface(ABC):
    @abstractmethod
    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        sort: SortField = "name",
        order: SortOrder = "asc",
    ) -> ProductPage:
        pass


class ProductClient(ProductClientInterface):
    def __init__(self, db_session: AsyncSession):
        self.product_service = ProductService(db_session)

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        sort: SortField = "name",
        order: SortOrder = "asc",
    ) -> ProductPage:
        return await self.product_service.list_products(
            page=page, page_size=page_size, q=q, sort=sort, order=order
        )
