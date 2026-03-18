from functools import lru_cache
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from oban import Oban

from src.config.settings import get_settings
from src.util.database_manager import DatabaseManager
from src.util.job_manager import JobManager
from src.dao.order_dao import OrderDAO
from src.service.order_service import OrderService


settings = get_settings()

@lru_cache()
def get_database_manager() -> DatabaseManager:
    return DatabaseManager(settings.database_url)

@lru_cache()
def get_oban() -> Oban:
    """
    Oban instance for API service.
    No queues defined - only used for job enqueueing.
    """
    return Oban(pool=Oban.create_pool(dsn=settings.database_url))

def get_db() -> Generator[Session, None, None]:
    db_manager = get_database_manager()
    yield from db_manager.get_session()

def get_job_manager(
    session: Session = Depends(get_db),
    oban: Oban = Depends(get_oban)
) -> JobManager:
    return JobManager(oban=oban, session=session)


def get_order_dao(db: Session = Depends(get_db)) -> OrderDAO:
    return OrderDAO(db)


def get_order_service(
    order_dao: OrderDAO = Depends(get_order_dao),
    job_manager: JobManager = Depends(get_job_manager)
) -> OrderService:
    return OrderService(order_dao, job_manager)
