from pydantic import BaseModel


class MealOrderArgs(BaseModel):
    order_id: str
    menu_item_id: str
    metadata: dict = {}


    @property
    def has_special_instructions(self):
        return self.metadata != {}