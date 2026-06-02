"""add public_uuid to tasks

Revision ID: 015
Revises: 014
Create Date: 2026-06-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '015'
down_revision: Union[str, None] = '014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('public_uuid', sa.String(36), nullable=True, unique=True))
    op.create_index('ix_tasks_public_uuid', 'tasks', ['public_uuid'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_tasks_public_uuid', table_name='tasks')
    op.drop_column('tasks', 'public_uuid')
