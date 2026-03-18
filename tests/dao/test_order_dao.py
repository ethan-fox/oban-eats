from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.model.db.base import Base
from src.model.db.order_orm import OrderORM
from src.dao.order_dao import OrderDAO


class TestOrderDAO:
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.dao = OrderDAO(self.session)

    def teardown_method(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_order_with_valid_data(self):
        order = OrderORM(table_id="table-1")

        created_order = self.dao.create(order)

        assert created_order.id is not None
        assert created_order.table_id == "table-1"
        assert created_order.created_at is not None

    def test_find_by_id_returns_order(self):
        order = OrderORM(table_id="table-2")
        created_order = self.dao.create(order)
        self.session.commit()

        found_order = self.dao.find_by_id(created_order.id)

        assert found_order is not None
        assert found_order.id == created_order.id
        assert found_order.table_id == "table-2"

    def test_find_by_id_returns_none_for_nonexistent_order(self):
        import uuid
        nonexistent_id = uuid.uuid4()

        found_order = self.dao.find_by_id(nonexistent_id)

        assert found_order is None
