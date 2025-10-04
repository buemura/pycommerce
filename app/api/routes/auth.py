from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.di_container import make_user_client
from app.modules.user.model import User
from app.modules.user.schemas import RegisterIn, LoginIn, UserPublic, LoginOut
from app.shared.db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=201)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)):
    client = make_user_client(session)
    return await client.create_user(name=body.name, email=body.email, password=body.password)


@router.post("/login", response_model=LoginOut)
async def login(
    body: LoginIn,
    session: AsyncSession = Depends(get_session),
):
    client = make_user_client(session)
    return await client.generate_access_token(email=body.email, password=body.password)


@router.get("/me", response_model=UserPublic)
async def read_current_user(user: User = Depends(get_current_user)):
    return user
