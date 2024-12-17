"""Creation of ReviewModel and New column in AgentModel

Revision ID: 1e263a9e7cda
Revises: 79198bc2980f
Create Date: 2024-12-10 10:39:24.075839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e263a9e7cda'
down_revision: Union[str, None] = '79198bc2980f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ReviewModel',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['AgentModel.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['UserModel.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('ReviewModel')
