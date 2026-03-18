from fastapi import FastAPI
from src.config.settings import get_settings
from src.config.middleware import apply_middleware
from src.router import health_router, order_router


def create_app() -> FastAPI:
    """
    API service application factory.
    Only handles REST endpoints - does NOT process jobs.
    """
    settings = get_settings()
    app = FastAPI(title=settings.api_title)

    apply_middleware(app, settings)

    app.include_router(health_router.router)
    app.include_router(order_router.router)

    return app


app = create_app()
