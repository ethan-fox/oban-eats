"""create_order_table

Revision ID: 00_02_00
Revises: 00_01_00
Create Date: 2024-01-01 12:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '00_02_00'
down_revision = '00_01_00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'order',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('table_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('idx_order_table_id', 'order', ['table_id'])


def downgrade() -> None:
    op.drop_index('idx_order_table_id')
    op.drop_table('order')
