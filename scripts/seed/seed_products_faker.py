import asyncio
import random
from typing import List, Dict

from faker import Faker
from sqlalchemy import insert

from app.shared.db import AsyncSessionLocal
from app.modules.product.model import Product


TOTAL = 500
BATCH_SIZE = 100  # tune as needed


def make_unique_product_names(fake: Faker, count: int) -> List[str]:
    """Generate 'pretty unique' product names."""
    seen = set()
    names: List[str] = []
    while len(names) < count:
        # e.g., "Aurora Keyboard 742" / "Crimson Monitor 318"
        name = f"{fake.color_name()} {fake.word().title()} {random.randint(100, 999)}"
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def build_products(fake: Faker, count: int) -> List[Dict]:
    names = make_unique_product_names(fake, count)
    items: List[Dict] = []
    for name in names:
        description = fake.sentence(nb_words=12)
        price = round(random.uniform(9.99, 2999.99), 2)
        stock = random.randint(0, 500)
        items.append(
            {
                "name": name,
                "description": description,
                "price": price,
                "stock": stock,
            }
        )
    return items


async def seed_products(total: int = TOTAL, batch_size: int = BATCH_SIZE) -> None:
    fake = Faker()
    async with AsyncSessionLocal() as session:
        payload = build_products(fake, total)
        # Insert in batches for efficiency
        for i in range(0, len(payload), batch_size):
            batch = payload[i : i + batch_size]
            await session.execute(insert(Product).values(batch))
        await session.commit()
    print(f"✅ Seeded {total} products.")


if __name__ == "__main__":
    asyncio.run(seed_products())
