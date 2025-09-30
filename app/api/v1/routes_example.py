from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/items", tags=["items"])


class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)


class ItemOut(ItemIn):
    id: int


_DB: dict[int, ItemOut] = {}
_COUNTER = 0


@router.get("", response_model=list[ItemOut])
def list_items() -> list[ItemOut]:
    return list(_DB.values())


@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn) -> ItemOut:
    global _COUNTER
    _COUNTER += 1
    item = ItemOut(id=_COUNTER, **payload.model_dump())
    _DB[item.id] = item
    return item


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int) -> ItemOut:
    if item_id not in _DB:
        raise HTTPException(status_code=404, detail="Not found")
    return _DB[item_id]
