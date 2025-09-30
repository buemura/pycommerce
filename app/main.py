from fastapi import FastAPI

from app.api.routes.auth import auth_router
from app.shared.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(auth_router)
    return app


app = create_app()
