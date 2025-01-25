"""empty message

Revision ID: 45b09f1f44fd
Revises: 29a246a5a841
Create Date: 2025-01-21 16:22:05.188374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45b09f1f44fd'
down_revision: Union[str, None] = '29a246a5a841'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "PropertyDocumentModel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("document_url", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["PropertyModel.id"], ),
    )
    op.add_column(
        "PropertyModel",
        sa.Column("title", sa.String(), nullable=False),
    )
    op.add_column(
        "PropertyInfoModel",
        sa.Column("rooms", sa.Integer(), nullable=False),
    )
    op.add_column(
        "PropertyInfoModel",
        sa.Column("renovation", sa.String(), nullable=False),
    )
    op.add_column(
        "PropertyBuildingModel",
        sa.Column("gym", sa.Boolean(), nullable=False),
    )
    op.drop_column("PropertyInfoModel", "condition")


def downgrade() -> None:
    op.drop_table("PropertyDocumentModel")
    op.drop_column("PropertyModel", "title")
    op.drop_column("PropertyInfoModel", "rooms")
    op.drop_column("PropertyInfoModel", "renovation")
    op.drop_column("PropertyBuildingModel", "gym")
    op.add_column(
        "PropertyInfoModel",
        sa.Column("condition", sa.String(), nullable=False),
    )
