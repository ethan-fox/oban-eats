"""create_order_meals_table

Revision ID: 00_03_00
Revises: 00_02_00
Create Date: 2026-03-22 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '00_03_00'
down_revision = '00_02_00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'order_meals',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, primary_key=True),
        sa.Column('order_id', UUID(as_uuid=True), nullable=False),
        sa.Column('menu_item_id', sa.String(255), nullable=False),
        sa.Column('meal_metadata', JSONB, server_default='{}', nullable=False),
        sa.Column('state', sa.String(50), server_default="'pending'", nullable=False),
        sa.Column('job_xref', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_order_meals_order_id', 'order_meals', ['order_id'])
    op.create_index('idx_order_meals_job_xref', 'order_meals', ['job_xref'])


def downgrade() -> None:
    op.drop_index('idx_order_meals_job_xref')
    op.drop_index('idx_order_meals_order_id')
    op.drop_table('order_meals')
