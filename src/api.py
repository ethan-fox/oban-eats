from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

from src.config.settings import get_settings
from src.config.middleware import apply_middleware
from src.config.dependency import initialize_oban, cleanup_oban
from src.config.logging import configure_logging
from src.router import health_router, order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle: startup and shutdown."""
    # Startup
    configure_logging()
    await initialize_oban()
    yield
    # Shutdown
    await cleanup_oban()


def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(title=settings.api_title, lifespan=lifespan)

    apply_middleware(app, settings)

    app.include_router(health_router.router)
    app.include_router(order_router.router)

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    Instrumentator().instrument(app).expose(app)

    return app

app = create_app()

