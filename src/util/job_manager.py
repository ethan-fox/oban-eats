from oban import Oban, Job
from sqlalchemy.orm import Session


class JobManager:
    def __init__(self, oban: Oban, session: Session):
        self.oban = oban
        self.session = session

    def enqueue(self, job) -> Job:
        """
        Enqueue single job transactionally.
        Always uses enqueue_many() with session for atomicity.
        """
        jobs = self.oban.enqueue_many([job], conn=self.session)
        return jobs[0]

    def enqueue_many(self, jobs: list) -> list[Job]:
        """
        Enqueue multiple jobs transactionally.
        All jobs enqueued atomically with database session.
        """
        return self.oban.enqueue_many(jobs, conn=self.session)
