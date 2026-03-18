"""initial_oban_tables

Revision ID: 00_01_00
Revises:
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
from oban.schema import install_sql, uninstall_sql

revision = '00_01_00'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(install_sql())


def downgrade() -> None:
    op.execute(uninstall_sql())
