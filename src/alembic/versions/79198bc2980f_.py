"""Initial revision

Revision ID: 79198bc2980f
Revises: 
Create Date: 2024-11-01 15:33:04.163929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79198bc2980f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'UserModel',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )



def downgrade() -> None:
    op.drop_table('users')
