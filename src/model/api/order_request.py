from pydantic import BaseModel


class MealItem(BaseModel):
    menu_item_id: str
    metadata: dict = {}


class CreateOrderRequest(BaseModel):
    table_id: str
    meals: list[MealItem]
