import logging

from src.dao.order_dao import OrderDAO
from src.model.api.order_request import CreateOrderRequest
from src.util.job_manager import JobManager
from src.model.db.order_orm import OrderORM
from src.model.view.order_view import OrderCreatedView
from src.worker.meal_order_worker import MealOrderWorker


logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, order_dao: OrderDAO, job_manager: JobManager):
        self.order_dao = order_dao
        self.job_manager = job_manager

    async def create_order(self, order_request: CreateOrderRequest) -> OrderCreatedView:
        """
        Create order and enqueue meal preparation jobs.
        Transactional: order and all meal jobs committed atomically.
        """

        logger.info(f"Got new order for table '{order_request.table_id}'")

        order = OrderORM(table_id=order_request.table_id)
        created_order = await self.order_dao.create(order)

        prepared_jobs = [
            MealOrderWorker.new({
                'order_id': str(created_order.id),
                'menu_item_id': meal.menu_item_id,
                'metadata': meal.metadata
            })
            for meal in order_request.meals
        ]

        await self.job_manager.enqueue_many(prepared_jobs)

        logger.info(f"Ordered {len(prepared_jobs)} meal(s) for table '{order_request.table_id}'")

        return OrderCreatedView(
            order_id=created_order.id,
            table_id=created_order.table_id,
            created_at=created_order.created_at,
            meals_count=len(prepared_jobs)
        )
