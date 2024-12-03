"""Initial migration

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

def upgrade():
    op.create_table('UserModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('bio', sa.String(), nullable=True),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('is_confirmed', sa.Boolean(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('AgentModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('serial_number', sa.String(), nullable=False),
    sa.Column('company', sa.String(), nullable=True),
    sa.Column('experience', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['UserModel.id'],),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ListingModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['AgentModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PropertyModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.Column('is_sold', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('listing_id', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['listing_id'], ['ListingModel.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['AgentModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ApprovalModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['PropertyModel.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['UserModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PropertyImageModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['PropertyModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('LocationModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['PropertyModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PropertyInfoModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('total_area', sa.Float(), nullable=False),
    sa.Column('living_area', sa.Float(), nullable=False),
    sa.Column('bedrooms', sa.Integer(), nullable=False),
    sa.Column('living_rooms', sa.Integer(), nullable=False),
    sa.Column('floor', sa.Integer(), nullable=False),
    sa.Column('floors', sa.Integer(), nullable=False),
    sa.Column('district', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['PropertyModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('UserImageModel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['UserModel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserImageModel')
    op.drop_table('PropertyInfoModel')
    op.drop_table('LocationModel')
    op.drop_table('PropertyImageModel')
    op.drop_table('PropertyModel')
    op.drop_table('ListingModel')
    op.drop_table('ApprovalModel')
    op.drop_table('AgentModel')
    op.drop_table('UserModel')
    # ### end Alembic commands ###