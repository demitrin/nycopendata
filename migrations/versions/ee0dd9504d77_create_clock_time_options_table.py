"""create clock_time_options table

Revision ID: ee0dd9504d77
Revises: 
Create Date: 2023-11-10 14:38:08.976529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision: str = 'ee0dd9504d77'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'clock_time_options',
        sa.Column('id', sa.String(), primary_key=True, default=str(uuid.uuid4())),
        sa.Column('clock_time', sa.Integer, nullable=False),
        sa.Column('measure_column_value', sa.DECIMAL, nullable=False),
        sa.Column('measure_columns', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('category_columns', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('dataset', sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('clock_time_options')
