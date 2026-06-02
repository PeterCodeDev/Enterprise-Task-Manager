"""add subtasks table

Revision ID: 006
Revises: 005
Create Date: 2026-06-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'subtasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('texto', sa.String(500), nullable=False),
        sa.Column('completada', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_subtasks_task_id', 'subtasks', ['task_id'])


def downgrade() -> None:
    op.drop_table('subtasks')
