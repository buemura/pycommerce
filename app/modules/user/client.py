from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.model import User
from app.modules.user.schemas import LoginOut
from app.modules.user.service import UserService


class UserClientInterface(ABC):
    @abstractmethod
    async def get_user(self, user_id: str) -> User:
        pass

    @abstractmethod
    async def create_user(self, name: str, email: str, password: str) -> User:
        pass

    @abstractmethod
    async def generate_access_token(self, email: str, password: str) -> LoginOut:
        pass


class UserClient(UserClientInterface):
    def __init__(self, db_session: AsyncSession):
        self.user_service = UserService(db_session=db_session)

    async def get_user(self, user_id: str) -> User:
        return await self.user_service.get_user(user_id)

    async def create_user(self, name: str, email: str, password: str) -> User:
        return await self.user_service.create_user(name, email, password)

    async def generate_access_token(self, email: str, password: str) -> LoginOut:
        return await self.user_service.generate_access_token(email, password)
