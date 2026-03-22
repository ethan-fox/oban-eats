"""
Application factory for creating FastAPI app instances.
Supports multiple deployment modes via MODE environment variable.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

from src.config.settings import get_settings
from src.config.app_mode import AppMode
from src.config.dependency import initialize_app_context, cleanup_app_context
from src.config.logging import configure_logging


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Shared across all deployment modes.
    """
    configure_logging()
    await initialize_app_context()
    yield
    await cleanup_app_context()


def create_app() -> FastAPI:
    """
    Create FastAPI application instance.

    - API => REST API for user-invoked actions
    - WORKER => Oban Jobs processing
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        lifespan=app_lifespan
    )

    # Mount routes based on MODE
    if settings.mode == AppMode.API:
        from src.config.middleware import apply_middleware
        from src.router import health_router, order_router

        apply_middleware(app, settings)
        app.include_router(health_router.router)
        app.include_router(order_router.router)

        # Mount Prometheus metrics
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        Instrumentator().instrument(app).expose(app)
    elif settings.mode == AppMode.WORKER:
        # No HTTP routes - workers poll Oban queues
        # FastAPI app only used for lifecycle management (startup/shutdown)
        pass
    else:
        # Future modes (listener, etc.)
        pass

    return app
