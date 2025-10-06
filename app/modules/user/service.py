from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.model import User
from app.modules.user.schemas import LoginOut
from app.shared.security import generate_access_token, hash_password, verify_password


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_user(self, user_id: str) -> User:
        user = await self.session.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def create_user(self, name: str, email: str, password: str) -> User:
        existing = await self.session.scalar(select(User).where(User.email == email))
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            name=name,
            email=email,
            password=hash_password(password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def generate_access_token(self, email: str, password: str) -> LoginOut:
        user = await self.session.scalar(select(User).where(User.email == email))

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = generate_access_token(subject=user.id)
        return LoginOut(access_token=token)
