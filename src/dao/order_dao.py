from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.model.db.order_orm import OrderORM
from uuid import UUID


class OrderDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, order: OrderORM) -> OrderORM:
        """
        Create new order record.

        Note: flush() writes to DB and retrieves the generated UUID
        without committing the transaction. This allows us to use
        the order ID for creating jobs in the same transaction.
        """
        self.db.add(order)
        await self.db.flush()
        return order

    async def find_by_id(self, order_id: UUID) -> OrderORM | None:
        """Find order by ID."""
        result = await self.db.execute(select(OrderORM).filter(OrderORM.id == order_id))
        return result.scalar_one_or_none()
