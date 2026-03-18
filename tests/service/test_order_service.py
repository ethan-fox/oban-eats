from unittest.mock import MagicMock
from src.service.order_service import OrderService
from src.dao.order_dao import OrderDAO
from src.util.job_manager import JobManager
from src.model.db.order_orm import OrderORM
import uuid
from datetime import datetime


class TestOrderService:
    def setup_method(self):
        self.mock_order_dao = MagicMock(spec=OrderDAO)
        self.mock_job_manager = MagicMock(spec=JobManager)
        self.service = OrderService(self.mock_order_dao, self.mock_job_manager)

    def test_create_order_creates_order_record(self):
        mock_order = OrderORM(table_id="table-1")
        mock_order.id = uuid.uuid4()
        mock_order.created_at = datetime.now()
        self.mock_order_dao.create.return_value = mock_order

        meals = [
            {"menu_item_id": "burger", "metadata": {}},
            {"menu_item_id": "fries", "metadata": {}}
        ]

        result = self.service.create_order("table-1", meals)

        self.mock_order_dao.create.assert_called_once()
        assert result.order_id == mock_order.id
        assert result.table_id == "table-1"
        assert result.meals_count == 2

    def test_create_order_enqueues_correct_number_of_jobs(self):
        mock_order = OrderORM(table_id="table-2")
        mock_order.id = uuid.uuid4()
        mock_order.created_at = datetime.now()
        self.mock_order_dao.create.return_value = mock_order

        meals = [
            {"menu_item_id": "burger", "metadata": {}},
            {"menu_item_id": "salad", "metadata": {}},
            {"menu_item_id": "fries", "metadata": {}}
        ]

        self.service.create_order("table-2", meals)

        self.mock_job_manager.enqueue_many.assert_called_once()
        jobs = self.mock_job_manager.enqueue_many.call_args[0][0]
        assert len(jobs) == 3

    def test_create_order_includes_metadata_in_jobs(self):
        mock_order = OrderORM(table_id="table-3")
        mock_order.id = uuid.uuid4()
        mock_order.created_at = datetime.now()
        self.mock_order_dao.create.return_value = mock_order

        meals = [
            {"menu_item_id": "burger", "metadata": {"no_onions": True}}
        ]

        self.service.create_order("table-3", meals)

        self.mock_job_manager.enqueue_many.assert_called_once()
        jobs = self.mock_job_manager.enqueue_many.call_args[0][0]
        assert jobs[0].args["metadata"] == {"no_onions": True}
