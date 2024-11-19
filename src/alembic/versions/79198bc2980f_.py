"""User models

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
    # Create UserModel table
    op.create_table(
        'UserModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('bio', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_confirmed', sa.Boolean(), default=False),
        sa.Column('role', sa.String(), nullable=True, default="buyer"),
        sa.Column('level', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create AgentModel table
    op.create_table(
        'AgentModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('serial_number', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=True)
    )
    # Create ListingModel table
    op.create_table(
        'ListingModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('AgentModel.id'), nullable=False)
    )

    # Create PropertyModel table
    op.create_table(
        'PropertyModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('approved', sa.Boolean(), default=False),
        sa.Column('is_sold', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('listing_id', sa.Integer(), sa.ForeignKey('ListingModel.id'), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('AgentModel.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create ApprovalModel table
    op.create_table(
        'ApprovalModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


    # Create PropertyImageModel table
    op.create_table(
        'PropertyImageModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
    )

    # Create LocationModel table
    op.create_table(
        'LocationModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False)
    )

    # Create PropertyInfoModel table
    op.create_table(
        'PropertyInfoModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('total_area', sa.Float(), nullable=False),
        sa.Column('living_area', sa.Float(), nullable=False),
        sa.Column('bedrooms', sa.Integer(), nullable=False),
        sa.Column('living_rooms', sa.Integer(), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('floors', sa.Integer(), nullable=False),
        sa.Column('district', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False)
    )

def downgrade() -> None:
    # Drop PropertyInfoModel table
    op.drop_table('PropertyInfoModel')

    # Drop LocationModel table
    op.drop_table('LocationModel')

    # Drop PropertyImageModel table
    op.drop_table('PropertyImageModel')

    # Drop PropertyModel table
    op.drop_table('PropertyModel')

    # Drop ListingModel table
    op.drop_table('ListingModel')

    # Drop ApprovalModel table
    op.drop_table('ApprovalModel')

    # Drop AgentModel table
    op.drop_table('AgentModel')

    # Drop UserModel table
    op.drop_table('UserModel')
