"""Added more columns

Revision ID: d160a53763d9
Revises: d232134c9bf6
Create Date: 2023-11-15 19:41:42.814119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd160a53763d9'
down_revision: Union[str, None] = 'd232134c9bf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clock_time_options', sa.Column('prompt', sa.String(), nullable=True))
    op.add_column('clock_time_options', sa.Column('department', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clock_time_options', 'department')
    op.drop_column('clock_time_options', 'prompt')
    # ### end Alembic commands ###
