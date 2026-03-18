from unittest.mock import MagicMock
from oban import Oban, Job
from src.util.job_manager import JobManager


class TestJobManager:
    def setup_method(self):
        self.mock_oban = MagicMock(spec=Oban)
        self.mock_session = MagicMock()
        self.job_manager = JobManager(self.mock_oban, self.mock_session)

    def test_enqueue_calls_enqueue_many_with_session(self):
        mock_job = MagicMock(spec=Job)
        self.mock_oban.enqueue_many.return_value = [mock_job]

        result = self.job_manager.enqueue(mock_job)

        self.mock_oban.enqueue_many.assert_called_once_with([mock_job], conn=self.mock_session)
        assert result == mock_job

    def test_enqueue_many_passes_correct_parameters_to_oban(self):
        mock_jobs = [MagicMock(spec=Job), MagicMock(spec=Job)]
        self.mock_oban.enqueue_many.return_value = mock_jobs

        result = self.job_manager.enqueue_many(mock_jobs)

        self.mock_oban.enqueue_many.assert_called_once_with(mock_jobs, conn=self.mock_session)
        assert result == mock_jobs
