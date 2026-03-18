import pytest
from unittest.mock import MagicMock, patch
from src.worker.meal_order_worker import MealOrderWorker


class TestMealOrderWorker:
    def setup_method(self):
        self.worker = MealOrderWorker()

    @pytest.mark.asyncio
    @patch('time.sleep')
    async def test_process_with_sample_order_payload(self, mock_sleep):
        mock_job = MagicMock()
        mock_job.args = {
            "order_id": "test-uuid-123",
            "menu_item_id": "burger",
            "metadata": {"no_onions": True}
        }

        result = await self.worker.process(mock_job)

        mock_sleep.assert_called_once_with(1)
        assert result["status"] == "completed"
        assert result["order_id"] == "test-uuid-123"

    @pytest.mark.asyncio
    @patch('time.sleep')
    @patch('logging.info')
    async def test_logging_output_includes_order_id(self, mock_logging, mock_sleep):
        mock_job = MagicMock()
        mock_job.args = {
            "order_id": "test-uuid-456",
            "menu_item_id": "salad",
            "metadata": {}
        }

        await self.worker.process(mock_job)

        assert mock_logging.call_count == 2
        first_call_args = mock_logging.call_args_list[0][0][0]
        second_call_args = mock_logging.call_args_list[1][0][0]

        assert "test-uuid-456" in first_call_args
        assert "salad" in first_call_args
        assert "Completed meal" in second_call_args
