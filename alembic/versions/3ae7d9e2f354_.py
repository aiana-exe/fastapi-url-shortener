"""empty message

Revision ID: 3ae7d9e2f354
Revises: 52c244f97f46
Create Date: 2024-07-04 14:14:10.804626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ae7d9e2f354'
down_revision: Union[str, None] = '52c244f97f46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'urls', ['original_url'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'urls', type_='unique')
    # ### end Alembic commands ###
