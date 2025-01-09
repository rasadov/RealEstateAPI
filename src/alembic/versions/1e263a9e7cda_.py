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


def upgrade():
    # Create ListingModel table
    op.create_table(
        'ListingModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('AgentModel.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
    )

    # Create ListingImageModel table
    op.create_table(
        'ListingImageModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('listing_id', sa.Integer(), sa.ForeignKey('ListingModel.id'), nullable=False),
    )

def downgrade():
    # Drop tables in reverse order of creation
    op.drop_table('ListingImageModel')
    op.drop_table('ListingModel')
