import asyncio
import json
from pathlib import Path
from sqlalchemy import select

from app.shared.db import AsyncSessionLocal
from app.modules.product.model import Product


DATA_FILE = Path(__file__).parent.parent / "seed" / "products.json"


async def seed_products():
    async with AsyncSessionLocal() as session:
        products = json.loads(DATA_FILE.read_text())

        for data in products:
            # check if already exists by name
            stmt = select(Product).where(Product.name == data["name"])
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                print(f"Skipping existing product: {existing.name}")
                continue

            product = Product(**data)
            session.add(product)
            print(f"Added product: {product.name}")

        await session.commit()
    print("✅ Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_products())
