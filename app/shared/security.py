from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

from app.shared.config import settings


pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(raw: str) -> str:
    """
    Hash a password.
    """
    return pwd_ctx.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """
    Verify a hashed password.
    """
    return pwd_ctx.verify(raw, hashed)


def generate_access_token(subject: str | int, expires_minutes: int | None = None) -> str:
    """
    Generate a JWT token.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
