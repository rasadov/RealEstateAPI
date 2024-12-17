"""Create report models and remove is_active column

Revision ID: 1b1a7b5cca12
Revises: 29a246a5a841
Create Date: 2024-12-16 17:32:49.472769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b1a7b5cca12'
down_revision: Union[str, None] = '29a246a5a841'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "PropertyReportModel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["PropertyModel.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["UserModel.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "AgentReportModel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["AgentModel.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["UserModel.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("AgentReportModel")
    op.drop_table("PropertyReportModel")
