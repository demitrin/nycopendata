"""Add columns for aggs

Revision ID: d232134c9bf6
Revises: d0b217ea82ec
Create Date: 2023-11-14 14:48:52.321016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd232134c9bf6'
down_revision: Union[str, None] = 'd0b217ea82ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clock_time_options', sa.Column('category_columns_values', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('clock_time_options', sa.Column('aggregate_function', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clock_time_options', 'aggregate_function')
    op.drop_column('clock_time_options', 'category_columns_values')
    # ### end Alembic commands ###