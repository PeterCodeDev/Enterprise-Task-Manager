"""add tiempo_acumulado to tasks

Revision ID: 012
Revises: 011
Create Date: 2026-06-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('tiempo_acumulado', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('tasks', 'tiempo_acumulado')
