from fastapi import FastAPI
from app.api.v1.routes_example import router as items_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok"}

    app.include_router(items_router)
    return app


app = create_app()
