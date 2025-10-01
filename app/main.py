from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.products import router as products_router
from app.api.routes.orders import router as orders_router
from app.shared.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    app.include_router(auth_router)
    app.include_router(products_router)
    app.include_router(orders_router)

    return app


app = create_app()
