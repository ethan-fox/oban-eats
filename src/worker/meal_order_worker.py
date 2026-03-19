from oban import worker
from random import randint
import time
import logging

from src.model.worker.meal_order_args import MealOrderArgs

logger = logging.getLogger(__name__)


@worker(queue="low_priority")
class MealOrderWorker:
    async def process(self, job):
        """
        Simulate meal preparation.
        Logs order ID and simulates 1 second of cooking time.
        """
        args = MealOrderArgs(**job.args)

        logger.info(f"Received new meal order for Order ID {args.order_id} (menu item: {args.menu_item_id})")
        
        if args.has_special_instructions:
            logger.info(f"Special instructions: {args.metadata}")

        # For example - simulates variant-time processing 
        time.sleep(randint(0, 9))

        logger.info(f"Completed meal for Order ID {args.order_id}")
        return {"status": "completed", "order_id": args.order_id}
