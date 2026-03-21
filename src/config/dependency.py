import logging
from typing import AsyncGenerator
from fastapi import Depends
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import AsyncSession
from oban import Oban

from src.config.settings import get_settings
from src.config.app_mode import AppMode
from src.util.database_manager import DatabaseManager
from src.util.job_manager import JobManager
from src.dao.order_dao import OrderDAO
from src.service.order_service import OrderService

logger = logging.getLogger(__name__)

# Global singletons
_database_manager: DatabaseManager | None = None
_oban_pool: AsyncConnectionPool | None = None
_oban: Oban | None = None


async def initialize_app_context() -> None:
    """
    Initialize global application context.
    Called during app startup. Behavior controlled by MODE environment variable.
    """
    global _database_manager, _oban_pool, _oban

    settings = get_settings()

    logger.info(f"Initializing application in MODE={settings.mode}")

    # Initialize database manager
    _database_manager = DatabaseManager(settings.database_url)

    # Initialize Oban pool
    _oban_pool = await Oban.create_pool(dsn=settings.database_url)

    # Configure Oban based on MODE
    if settings.mode == AppMode.WORKER:
        # Worker mode: enable queue processing
        queues = {"high_priority": 1, "low_priority": 1}
        lifeline = {"interval": 15, "rescue_after": 60}
        _oban = Oban(pool=_oban_pool, queues=queues, lifeline=lifeline, metrics=True)
        await _oban.start()
    else:
        # API mode - no need to `start` nor supply addt'l kwargs 
        _oban = Oban(pool=_oban_pool, queues=None, metrics=True)
        
    logger.info(f"Starting App in {settings.mode} mode")


async def cleanup_app_context() -> None:
    """
    Cleanup global application context.
    Called during app shutdown.
    """
    global _oban_pool, _oban

    logger.info("Cleaning up application context")

    if _oban is not None:
        await _oban.stop()
        _oban = None

    if _oban_pool is not None:
        await _oban_pool.close()
        _oban_pool = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager singleton."""
    if _database_manager is None:
        raise RuntimeError("Application context not initialized")
    return _database_manager


def get_oban() -> Oban:
    """Get global Oban singleton."""
    if _oban is None:
        raise RuntimeError("Application context not initialized")
    return _oban

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session for FastAPI routes (via Depends)."""
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session


def get_job_manager(
    session: AsyncSession = Depends(get_db),
    oban: Oban = Depends(get_oban)
) -> JobManager:
    """Provide JobManager for FastAPI routes (via Depends)."""
    return JobManager(oban=oban, session=session)


def get_order_dao(db: AsyncSession = Depends(get_db)) -> OrderDAO:
    """Provide OrderDAO for FastAPI routes (via Depends)."""
    return OrderDAO(db)


def get_order_service(
    order_dao: OrderDAO = Depends(get_order_dao),
    job_manager: JobManager = Depends(get_job_manager)
) -> OrderService:
    """Provide OrderService for FastAPI routes (via Depends)."""
    return OrderService(order_dao, job_manager)
