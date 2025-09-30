from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginOut(BaseModel):
    access_token: str


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True  # ORM mode
