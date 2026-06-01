"""add fecha_vencimiento to tasks

Revision ID: 004
Revises: 003
Create Date: 2026-06-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'fecha_vencimiento')
