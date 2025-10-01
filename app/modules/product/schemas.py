from pydantic import BaseModel, Field
from typing import List


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    class Config:
        from_attributes = True  # ORM mode


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=200)
    total: int
    pages: int


class ProductPage(BaseModel):
    data: List[ProductOut]
    meta: PaginationMeta
