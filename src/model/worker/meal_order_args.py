from pydantic import BaseModel


class MealOrderArgs(BaseModel):
    order_id: str
    menu_item_id: str
    metadata: dict = {}
