from sqlalchemy.orm import Session
from src.model.db.order_orm import OrderORM
from uuid import UUID


class OrderDAO:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: OrderORM) -> OrderORM:
        """
        Create new order record.

        Note: flush() writes to DB and retrieves the generated UUID
        without committing the transaction. This allows us to use
        the order ID for creating jobs in the same transaction.
        """
        self.db.add(order)
        self.db.flush()
        return order

    def find_by_id(self, order_id: UUID) -> OrderORM | None:
        """Find order by ID."""
        return self.db.query(OrderORM).filter(OrderORM.id == order_id).first()
