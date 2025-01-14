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
    # Create UserModel table
    op.create_table(
        'UserModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('bio', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_confirmed', sa.Boolean(), default=False),
        sa.Column('role', sa.String(), nullable=True, default='buyer'),
        sa.Column('level', sa.Integer(), nullable=False, default=0),
    )

    # Create UserImageModel table
    op.create_table(
        'UserImageModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True, default='https://flattybucket.s3.us-east-1.amazonaws.com/uploads/user.jpg'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create AgentModel table
    op.create_table(
        'AgentModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('serial_number', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('experience', sa.Float(), nullable=True),
        sa.Column('sales', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create ReviewModel table
    op.create_table(
        'ReviewModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('AgentModel.id'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
    )

    # Create AgentReportModel table
    op.create_table(
        'AgentReportModel',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('AgentModel.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('UserModel.id'), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
    )

def downgrade():
    # Drop tables in reverse order of creation
    op.drop_table('AgentReportModel')
    op.drop_table('ReviewModel')
    op.drop_table('ApprovalModel')
    op.drop_table('AgentModel')
    op.drop_table('UserImageModel')
    op.drop_table('UserModel')
