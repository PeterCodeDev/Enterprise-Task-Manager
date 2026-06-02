"""add prioridad to tasks

Revision ID: 005
Revises: 004
Create Date: 2026-06-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('prioridad', sa.String(10), nullable=False, server_default='media'))


def downgrade() -> None:
    op.drop_column('tasks', 'prioridad')
