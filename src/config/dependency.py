from functools import lru_cache
from typing import AsyncGenerator
from fastapi import Depends
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import AsyncSession
from oban import Oban

from src.config.settings import get_settings
from src.util.database_manager import DatabaseManager
from src.util.job_manager import JobManager
from src.dao.order_dao import OrderDAO
from src.service.order_service import OrderService


settings = get_settings()

# Singleton instances (initialized in app lifespan)
_oban_pool: AsyncConnectionPool | None = None
_oban_instance: Oban | None = None

@lru_cache()
def get_database_manager() -> DatabaseManager:
    return DatabaseManager(settings.database_url)

def get_oban() -> Oban:
    """Returns the singleton Oban instance."""
    if _oban_instance is None:
        raise RuntimeError("Oban not initialized. Ensure app lifespan has started.")
    return _oban_instance

async def initialize_oban() -> None:
    """Initialize Oban pool and instance. Call during app startup."""
    global _oban_pool, _oban_instance
    if _oban_pool is None:
        _oban_pool = await Oban.create_pool(dsn=settings.database_url)
        _oban_instance = Oban(pool=_oban_pool)

async def cleanup_oban() -> None:
    """Close Oban pool. Call during app shutdown."""
    global _oban_pool, _oban_instance
    if _oban_pool is not None:
        await _oban_pool.close()
        _oban_pool = None
        _oban_instance = None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session

async def get_job_manager(
    session: AsyncSession = Depends(get_db),
    oban: Oban = Depends(get_oban)
) -> JobManager:
    return JobManager(oban=oban, session=session)


async def get_order_dao(db: AsyncSession = Depends(get_db)) -> OrderDAO:
    return OrderDAO(db)


async def get_order_service(
    order_dao: OrderDAO = Depends(get_order_dao),
    job_manager: JobManager = Depends(get_job_manager)
) -> OrderService:
    return OrderService(order_dao, job_manager)
