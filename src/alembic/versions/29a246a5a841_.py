"""empty message

Revision ID: 29a246a5a841
Revises: 1e263a9e7cda
Create Date: 2024-12-11 15:21:56.626253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29a246a5a841'
down_revision: Union[str, None] = '1e263a9e7cda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create PropertyModel table
    op.create_table(
        'PropertyModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('approved', sa.Boolean(), default=False),
        sa.Column('is_sold', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('listing_id', sa.Integer(), sa.ForeignKey('ListingModel.id'), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('AgentModel.id'), nullable=False),
    )

    # Create PropertyImageModel table
    op.create_table(
        'PropertyImageModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
    )

    # Create PropertyLocationModel table
    op.create_table(
        'PropertyLocationModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
    )

    # Create PropertyInfoModel table
    op.create_table(
        'PropertyInfoModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('apartment_area', sa.Float(), nullable=False),
        sa.Column('total_area', sa.Float(), nullable=False),
        sa.Column('kitchen_area', sa.Float(), nullable=False),
        sa.Column('living_area', sa.Float(), nullable=False),
        sa.Column('bathrooms', sa.Integer(), nullable=False),
        sa.Column('rooms', sa.Integer(), nullable=False),
        sa.Column('living_rooms', sa.Integer(), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('floors', sa.Integer(), nullable=False),
        sa.Column('district', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('balcony', sa.String(), nullable=False),
        sa.Column('view', sa.String(), nullable=False),
    )

    # Create PropertyBuildingModel table
    op.create_table(
        'PropertyBuildingModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('year_built', sa.Integer(), nullable=False),
        sa.Column('elevators', sa.Integer(), nullable=False),
        sa.Column('building_type', sa.String(), nullable=False),
        sa.Column('flooring_type', sa.String(), nullable=False),
        sa.Column('parking', sa.String(), nullable=False),
    )

    # Create PropertyReportModel table
    op.create_table(
        'PropertyReportModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
    )

    # Create ApprovalModel table
    op.create_table(
        'ApprovalModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
    )

    # Create PropertyLikeModel table
    op.create_table(
        'PropertyLikeModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('property_id', sa.Integer(), sa.ForeignKey('PropertyModel.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    # Drop tables in reverse order of creation
    op.drop_table('PropertyReportModel')
    op.drop_table('PropertyBuildingModel')
    op.drop_table('PropertyInfoModel')
    op.drop_table('PropertyLocationModel')
    op.drop_table('PropertyImageModel')
    op.drop_table('PropertyModel')
    op.drop_table('ApprovalModel')
