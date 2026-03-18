from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class OrderCreatedView(BaseModel):
    order_id: UUID
    table_id: str
    created_at: datetime
    meals_count: int

    class Config:
        from_attributes = True
