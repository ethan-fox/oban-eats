from pydantic import BaseModel
from uuid import UUID


class MealOrderArgs(BaseModel):
    order_id: UUID
    meal_id: UUID