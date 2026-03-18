from src.dao.order_dao import OrderDAO
from src.model.api.order_request import CreateOrderRequest
from src.util.job_manager import JobManager
from src.model.db.order_orm import OrderORM
from src.model.view.order_view import OrderCreatedView
from src.worker.meal_order_worker import MealOrderWorker
from src.model.worker.meal_order_args import MealOrderArgs


class OrderService:
    def __init__(self, order_dao: OrderDAO, job_manager: JobManager):
        self.order_dao = order_dao
        self.job_manager = job_manager

    def create_order(self, order_request: CreateOrderRequest) -> OrderCreatedView:
        """
        Create order and enqueue meal preparation jobs.
        Transactional: order and all meal jobs committed atomically.
        """
        order = OrderORM(table_id=order_request.table_id)
        created_order = self.order_dao.create(order)

        prepared_jobs = [
            MealOrderWorker.new(args={
                'order_id': str(created_order.id),
                'menu_item_id': meal.menu_item_id,
                'metadata': meal.metadata
            })
            for meal in order_request.meals
        ]

        enqueued_meals = self.job_manager.enqueue_many(prepared_jobs)

        return OrderCreatedView(
            order_id=created_order.id,
            table_id=created_order.table_id,
            created_at=created_order.created_at,
            meals_count=len(enqueued_meals)
        )
