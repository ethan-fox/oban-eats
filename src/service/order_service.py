import logging

from src.dao.order_dao import OrderDAO
from src.dao.order_meal_dao import OrderMealDAO
from src.model.api.order_request import CreateOrderRequest
from src.util.job_manager import JobManager
from src.model.db.order_orm import OrderORM
from src.model.db.order_meal_orm import OrderMealORM
from src.model.view.order_view import OrderCreatedView
from src.worker.meal_order_worker import MealOrderWorker


logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, order_dao: OrderDAO, order_meal_dao: OrderMealDAO, job_manager: JobManager):
        self.order_dao = order_dao
        self.order_meal_dao = order_meal_dao
        self.job_manager = job_manager

    async def create_order(self, order_request: CreateOrderRequest) -> OrderCreatedView:
        """
        Create order with meals and enqueue jobs.
        Race-condition free: meals created BEFORE jobs enqueued.
        """
        logger.info(f"Creating order for table '{order_request.table_id}'")

        order = OrderORM(table_id=order_request.table_id)
        created_order = await self.order_dao.create(order)

        meal_records = [
            OrderMealORM(
                order_id=created_order.id,
                menu_item_id=meal.menu_item_id,
                meal_metadata=meal.metadata,
                state='pending',
                job_xref=None
            )
            for meal in order_request.meals
        ]
        created_meals = await self.order_meal_dao.create_many(meal_records)

        prepared_jobs = [
            MealOrderWorker.new({
                'order_id': str(created_order.id),
                'meal_id': str(meal.id)
            })
            for meal in created_meals
        ]

        await self.job_manager.enqueue_many(prepared_jobs)

        logger.info(f"Enqueued {len(created_meals)} meal job(s) for order {created_order.id}")

        return OrderCreatedView(
            order_id=created_order.id,
            table_id=created_order.table_id,
            created_at=created_order.created_at,
            meals_count=len(created_meals)
        )
