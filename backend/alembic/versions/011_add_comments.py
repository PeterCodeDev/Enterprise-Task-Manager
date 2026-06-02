"""add comments table

Revision ID: 011
Revises: 010
Create Date: 2026-06-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('texto', sa.String(2000), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_comments_task_id', 'comments', ['task_id'])


def downgrade() -> None:
    op.drop_table('comments')
