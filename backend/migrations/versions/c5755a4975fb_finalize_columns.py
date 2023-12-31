"""Finalize columns

Revision ID: c5755a4975fb
Revises: 365fda0c5abc
Create Date: 2023-11-15 22:10:18.727210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5755a4975fb'
down_revision: Union[str, None] = '365fda0c5abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clock_time_options', 'dataset_name')
    op.drop_column('clock_time_options', 'department')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clock_time_options', sa.Column('department', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('clock_time_options', sa.Column('dataset_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
