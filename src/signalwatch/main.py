from fastapi import FastAPI

from signalwatch.api.routes import health
from signalwatch.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    app.include_router(health.router)
    app.include_router(health.router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
