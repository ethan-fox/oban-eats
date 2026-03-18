from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid as uuid_module
from src.model.db.base import Base


class OrderORM(Base):
    __tablename__ = "order"

    id: uuid_module.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid_module.uuid4)
    table_id: str = Column(String(255), nullable=False, index=True)
    created_at: datetime = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
