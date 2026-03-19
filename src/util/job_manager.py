import logging
from oban import Oban, Job
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self, oban: Oban, session: AsyncSession):
        self.oban = oban
        self.session = session

    async def enqueue_many(self, jobs: list) -> list[Job]:
        """
        Enqueue multiple jobs transactionally.
        All jobs enqueued atomically with database session.
        """

        logger.info(f"Enqueuing {len(jobs)} job(s)")
        return await self.oban.enqueue_many(jobs, conn=self.session)
