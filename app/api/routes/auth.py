from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.modules.user.model import User
from app.modules.user.schemas import RegisterIn, LoginIn, UserPublic, LoginOut
from app.shared.db import get_session
from app.shared.security import hash_password, verify_password, generate_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=201)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=body.name,
        email=body.email,
        password=hash_password(body.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=LoginOut)
async def login(
    body: LoginIn,
    session: AsyncSession = Depends(get_session),
):
    user = await session.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = generate_access_token(subject=user.id)
    return LoginOut(access_token=token)


@router.get("/me", response_model=UserPublic)
async def read_current_user(user: User = Depends(get_current_user)):
    return user
