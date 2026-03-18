from oban import worker
import time
import logging

from src.model.worker.meal_order_args import MealOrderArgs


@worker(queue="low_priority")
class MealOrderWorker:
    async def process(self, job):
        """
        Simulate meal preparation.
        Logs order ID and simulates 1 second of cooking time.
        """
        args = MealOrderArgs(**job.args)

        logging.info(f"Received new meal order for Order ID {args.order_id} (menu item: {args.menu_item_id})")

        time.sleep(1)

        logging.info(f"Completed meal for Order ID {args.order_id}")
        return {"status": "completed", "order_id": args.order_id}
