import logging
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from oban import Oban

from src.config.context import ObanEatsContext
from src.util.database_manager import DatabaseManager
from src.util.job_manager import JobManager
from src.dao.order_dao import OrderDAO
from src.dao.order_meal_dao import OrderMealDAO
from src.service.order_service import OrderService

logger = logging.getLogger(__name__)

# Get context singleton once at module level
_context = ObanEatsContext.get_instance()


async def initialize_app_context() -> None:
    """
    Initialize global application context.
    Called during app startup.
    """
    await _context.initialize()


async def cleanup_app_context() -> None:
    """
    Cleanup global application context.
    Called during app shutdown.
    """
    await _context.cleanup()


def get_database_manager() -> DatabaseManager:
    """Get global database manager singleton."""
    return _context.get_database_manager()


def get_oban() -> Oban:
    """Get global Oban singleton."""
    return _context.get_oban()

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


def get_order_meal_dao(db: AsyncSession = Depends(get_db)) -> OrderMealDAO:
    """Provide OrderMealDAO for FastAPI routes (via Depends)."""
    return OrderMealDAO(db)


def get_order_service(
    order_dao: OrderDAO = Depends(get_order_dao),
    order_meal_dao: OrderMealDAO = Depends(get_order_meal_dao),
    job_manager: JobManager = Depends(get_job_manager)
) -> OrderService:
    """Provide OrderService for FastAPI routes (via Depends)."""
    return OrderService(order_dao, order_meal_dao, job_manager)
