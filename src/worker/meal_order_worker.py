from oban import worker
from random import randint
import time
import logging

from src.config.context import ObanEatsContext
from src.dao.order_meal_dao import OrderMealDAO
from src.model.worker.meal_order_args import MealOrderArgs

logger = logging.getLogger(__name__)

_context = ObanEatsContext.get_instance()


@worker(queue="low_priority")
class MealOrderWorker:
    async def process(self, job):
        """
        Process meal preparation job.
        Fetches meal details from database, updates job_xref and state.
        """
        args = MealOrderArgs(**job.args)

        logger.info(f"Processing meal {args.meal_id} for order {args.order_id}")

        db_manager = _context.get_database_manager()

        async with db_manager.SessionLocal() as session:
            try:
                meal_dao = OrderMealDAO(db=session)

                meal = await meal_dao.find_by_id(args.meal_id)
                if not meal:
                    logger.error(f"Meal {args.meal_id} not found!")
                    raise ValueError(f"Meal {args.meal_id} does not exist")

                logger.info(f"Processing {meal.menu_item_id} (meal {args.meal_id})")

                meal.job_xref = str(job.id)
                await session.flush()
                logger.info(f"Claimed meal {args.meal_id} with job {job.id}")

                if meal.meal_metadata:
                    logger.info(f"Special instructions: {meal.meal_metadata}")

                time.sleep(randint(0, 9))

                meal.state = 'completed'
                await session.commit()

                logger.info(f"Completed {meal.menu_item_id} (meal {args.meal_id})")
                return {"status": "completed", "meal_id": str(args.meal_id)}

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to process meal {args.meal_id}: {e}")
                raise
