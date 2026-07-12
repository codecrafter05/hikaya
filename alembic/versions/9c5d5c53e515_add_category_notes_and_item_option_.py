"""add_category_notes_and_item_option_groups

Revision ID: 9c5d5c53e515
Revises: 6a1656d3e1b8
Create Date: 2026-07-12 10:19:11.571090

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '9c5d5c53e515'
down_revision: Union[str, None] = '6a1656d3e1b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('note_ar', sa.Text(), nullable=True))
    op.add_column('categories', sa.Column('note_en', sa.Text(), nullable=True))
    op.add_column(
        'menu_items',
        sa.Column('option_groups', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.alter_column('menu_items', 'option_groups', server_default=None)


def downgrade() -> None:
    op.drop_column('menu_items', 'option_groups')
    op.drop_column('categories', 'note_en')
    op.drop_column('categories', 'note_ar')
