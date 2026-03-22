from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.model.db.base import Base


class OrderMealORM(Base):
    __tablename__ = "order_meals"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = Column(String(255), nullable=False)
    meal_metadata = Column(JSONB, nullable=False, server_default="{}")
    state = Column(String(50), nullable=False, server_default="'pending'")
    job_xref = Column(String(255), nullable=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    order = relationship("OrderORM", back_populates="meals")
