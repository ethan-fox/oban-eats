from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.model.db.order_meal_orm import OrderMealORM
from uuid import UUID


class OrderMealDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, meals: list[OrderMealORM]) -> list[OrderMealORM]:
        """Bulk create meal records."""
        self.db.add_all(meals)
        await self.db.flush()
        return meals

    async def find_by_id(self, meal_id: UUID) -> OrderMealORM | None:
        """Find meal by ID."""
        result = await self.db.execute(
            select(OrderMealORM).filter(OrderMealORM.id == meal_id)
        )
        return result.scalar_one_or_none()

    async def update_state(self, meal_id: UUID, state: str, job_xref: str | None = None) -> OrderMealORM:
        """Update meal state and optionally set job_xref."""
        meal = await self.find_by_id(meal_id)
        if not meal:
            raise ValueError(f"Meal {meal_id} not found")

        meal.state = state
        if job_xref is not None:
            meal.job_xref = job_xref

        await self.db.flush()
        return meal
