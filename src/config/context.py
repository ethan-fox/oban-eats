import logging
from psycopg_pool import AsyncConnectionPool
from oban import Oban

from src.config.settings import get_settings
from src.config.app_mode import AppMode
from src.util.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ObanEatsContext:
    """Global application context singleton."""

    _instance: 'ObanEatsContext | None' = None

    def __init__(self):
        self.database_manager: DatabaseManager | None = None
        self.oban_pool: AsyncConnectionPool | None = None
        self.oban: Oban | None = None

    @classmethod
    def get_instance(cls) -> 'ObanEatsContext':
        """Get or create the global context singleton."""
        if cls._instance is None:
            cls._instance = ObanEatsContext()
        return cls._instance

    async def initialize(self) -> None:
        """
        Initialize global application context.
        Called during app startup. Behavior controlled by MODE environment variable.
        """
        settings = get_settings()

        logger.info(f"Initializing application in MODE={settings.mode}")

        self.database_manager = DatabaseManager(settings.database_url)

        self.oban_pool = await Oban.create_pool(dsn=settings.database_url)

        if settings.mode == AppMode.WORKER:
            queues = {"high_priority": 1, "low_priority": 1}
            lifeline = {"interval": 15, "rescue_after": 60}
            self.oban = Oban(pool=self.oban_pool, queues=queues, lifeline=lifeline, metrics=True)
            await self.oban.start()
        else:
            self.oban = Oban(pool=self.oban_pool, queues=None, metrics=True)

        logger.info(f"Starting App in {settings.mode} mode")

    async def cleanup(self) -> None:
        """
        Cleanup global application context.
        Called during app shutdown.
        """
        logger.info("Cleaning up application context")

        if self.oban is not None:
            await self.oban.stop()
            self.oban = None

        if self.oban_pool is not None:
            await self.oban_pool.close()
            self.oban_pool = None

    def get_database_manager(self) -> DatabaseManager:
        """Get database manager singleton."""
        if self.database_manager is None:
            raise RuntimeError("Application context not initialized")
        return self.database_manager

    def get_oban(self) -> Oban:
        """Get Oban singleton."""
        if self.oban is None:
            raise RuntimeError("Application context not initialized")
        return self.oban
