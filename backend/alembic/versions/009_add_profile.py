"""add profile fields to users

Revision ID: 009
Revises: 008
Create Date: 2026-06-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('nombre', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('bio', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('avatar_color', sa.String(7), server_default='#4361ee', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'nombre')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_color')
