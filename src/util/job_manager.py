from oban import Oban, Job
from sqlalchemy.ext.asyncio import AsyncSession


class JobManager:
    def __init__(self, oban: Oban, session: AsyncSession):
        self.oban = oban
        self.session = session

    async def enqueue(self, job) -> Job:
        """
        Enqueue single job transactionally.
        Uses session's connection for atomicity with DB operations.
        """
        jobs = await self.oban.enqueue_many([job], conn=self.session)
        return jobs[0]

    async def enqueue_many(self, jobs: list) -> list[Job]:
        """
        Enqueue multiple jobs transactionally.
        All jobs enqueued atomically with database session.
        """
        return await self.oban.enqueue_many(jobs, conn=self.session)
