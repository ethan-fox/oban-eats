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

# Singleton pool (initialized in app lifespan)
_oban_pool: AsyncConnectionPool | None = None

async def initialize_oban() -> None:
    """Initialize Oban connection pool. Call during app startup."""
    global _oban_pool
    if _oban_pool is None:
        _oban_pool = await Oban.create_pool(dsn=settings.database_url)

async def cleanup_oban() -> None:
    """Close Oban connection pool. Call during app shutdown."""
    global _oban_pool
    if _oban_pool is not None:
        await _oban_pool.close()
        _oban_pool = None

@lru_cache()
def get_database_manager() -> DatabaseManager:
    return DatabaseManager(settings.database_url)

@lru_cache()
def get_oban() -> Oban:
    """Returns a cached Oban instance using the singleton pool."""
    if _oban_pool is None:
        raise RuntimeError("Oban pool not initialized. Ensure app lifespan has started.")
    return Oban(pool=_oban_pool)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session

def get_job_manager(
    session: AsyncSession = Depends(get_db),
    oban: Oban = Depends(get_oban)
) -> JobManager:
    return JobManager(oban=oban, session=session)


def get_order_dao(db: AsyncSession = Depends(get_db)) -> OrderDAO:
    return OrderDAO(db)


def get_order_service(
    order_dao: OrderDAO = Depends(get_order_dao),
    job_manager: JobManager = Depends(get_job_manager)
) -> OrderService:
    return OrderService(order_dao, job_manager)
