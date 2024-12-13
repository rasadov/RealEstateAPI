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


def upgrade() -> None:
    op.drop_column("LocationModel", "is_active")
    op.add_column("LocationModel", sa.Column("district", sa.String(), nullable=True))
    op.add_column("LocationModel", sa.Column("address", sa.String(), nullable=True))
    op.add_column("LocationModel", sa.Column("is_active", sa.BOOLEAN(), nullable=True))

    op.create_table(
        "ListingImageModel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["ListingModel.id"], ),
        sa.PrimaryKeyConstraint("id")
    )

def downgrade() -> None:
    op.add_column("LocationModel", sa.Column("is_active", sa.BOOLEAN(), nullable=True))
    op.drop_column("LocationModel", "district")
    op.drop_column("LocationModel", "address")
    op.drop_table("ListingImageModel")
