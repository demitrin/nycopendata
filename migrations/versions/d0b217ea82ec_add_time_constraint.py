"""Add time constraint

Revision ID: d0b217ea82ec
Revises: ee0dd9504d77
Create Date: 2023-11-11 14:09:06.673313

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd0b217ea82ec'
down_revision: Union[str, None] = 'ee0dd9504d77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE clock_time_options
        ADD CONSTRAINT check_time_format
        CHECK (
            (clock_time % 100) BETWEEN 0 AND 60
            AND (clock_time / 100) BETWEEN 0 AND 24
        );
        """
    )

def downgrade() -> None:
    op.execute("ALTER TABLE clock_time_options DROP CONSTRAINT IF EXISTS check_time_format;")

